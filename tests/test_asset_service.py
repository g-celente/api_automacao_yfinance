"""
Testes unitários para o AssetService.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, date
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.Asset_service import AssetService


class TestAssetService(unittest.TestCase):
    """Testes para o AssetService."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.sample_ticker = "ITUB4.SA"
        self.sample_carteira_id = 1
        
        # Mock data for yfinance
        self.mock_yf_data = {
            'Close': [30.0, 31.0, 32.0, 31.5, 33.0],
            'Open': [29.5, 30.5, 31.5, 31.0, 32.5],
            'High': [30.5, 31.5, 32.5, 32.0, 33.5],
            'Low': [29.0, 30.0, 31.0, 31.0, 32.0],
            'Volume': [1000000, 1100000, 1200000, 1050000, 1300000]
        }
        
        # Create mock DataFrame with DatetimeIndex
        dates = pd.date_range('2024-01-01', periods=5, freq='D')
        self.mock_df = pd.DataFrame(self.mock_yf_data, index=dates)
    
    @patch('app.services.Asset_service.yf.Ticker')
    @patch('flask.g')
    @patch('app.services.Asset_service.db')
    @patch('app.services.Asset_service.Carteira')
    @patch('app.services.Asset_service.Cliente')
    @patch('app.services.Asset_service.Asset')
    def test_cadastrar_ativo_success(self, mock_asset, mock_cliente, mock_carteira, 
                                   mock_db, mock_g, mock_yf_ticker):
        """Testa o cadastro bem-sucedido de um ativo."""
        
        # Setup mocks
        mock_g.current_user_id = 1
        
        # Mock carteira query
        mock_carteira_instance = MagicMock()
        mock_carteira.query.join.return_value.filter.return_value.first.return_value = mock_carteira_instance
        
        # Mock yfinance
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = self.mock_df
        mock_yf_ticker.return_value = mock_ticker_instance
        
        # Mock Asset.exists_asset to return empty list
        mock_asset.exists_asset.return_value = []
        
        # Mock bulk insert
        mock_db.session.bulk_insert_mappings = MagicMock()
        mock_db.session.commit = MagicMock()
        
        # Test data
        data = {
            'ticker': 'ITUB4',
            'carteira_id': 1,
            'intervalo': '1d',
            'period': '3mo'
        }
        
        # Execute
        result, status_code = AssetService.cadastrar_ativo(data)
        
        # Assertions
        self.assertEqual(status_code, 201)
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['ticker'], 'ITUB4.SA')
        self.assertEqual(result['data']['records_inserted'], 5)
        
        # Verify database operations were called
        mock_db.session.bulk_insert_mappings.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    @patch('flask.g')
    @patch('app.services.Asset_service.Carteira')
    @patch('app.services.Asset_service.Cliente')
    def test_cadastrar_ativo_carteira_not_found(self, mock_cliente, mock_carteira, mock_g):
        """Testa o erro quando a carteira não é encontrada."""
        
        # Setup mocks
        mock_g.current_user_id = 1
        mock_carteira.query.join.return_value.filter.return_value.first.return_value = None
        
        # Test data
        data = {
            'ticker': 'ITUB4',
            'carteira_id': 999,
            'intervalo': '1d',
            'period': '3mo'
        }
        
        # Execute
        result, status_code = AssetService.cadastrar_ativo(data)
        
        # Assertions
        self.assertEqual(status_code, 404)
        self.assertFalse(result['success'])
        self.assertIn('not found', result['message'])
    
    def test_cadastrar_ativo_missing_ticker(self):
        """Testa o erro quando o ticker não é fornecido."""
        
        data = {
            'carteira_id': 1,
            'intervalo': '1d',
            'period': '3mo'
        }
        
        # Execute
        result, status_code = AssetService.cadastrar_ativo(data)
        
        # Assertions
        self.assertEqual(status_code, 400)
        self.assertFalse(result['success'])
        self.assertIn('Ticker is required', result['message'])
    
    @patch('flask.g')
    @patch('app.services.Asset_service.Asset')
    def test_calcular_indicadores_carteira_success(self, mock_asset, mock_g):
        """Testa o cálculo bem-sucedido de indicadores."""
        
        # Setup mocks
        mock_g.current_user_id = 1
        
        # Create mock asset data
        mock_assets = []
        tickers = ['ITUB4.SA', 'PETR4.SA', 'BOVA11.SA']
        
        for i, ticker in enumerate(tickers):
            for j in range(5):  # 5 days of data
                asset = MagicMock()
                asset.ticker = ticker
                asset.date = date(2024, 1, j+1)
                asset.close = 30.0 + i + j * 0.5  # Different prices for each asset/day
                mock_assets.append(asset)
        
        mock_asset.get_assets_by_carteira_admin.return_value = mock_assets
        
        # Execute
        result, status_code = AssetService.calcular_indicadores_carteira(1)
        
        # Assertions
        self.assertEqual(status_code, 200)
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('ativos_ordenados', result['data'])
        self.assertIn('retorno_esperado', result['data'])
        self.assertIn('desvio_padrao', result['data'])
        self.assertIn('beta', result['data'])
        self.assertIn('BOVA11.SA', result['data']['ativos_ordenados'])
    
    @patch('flask.g')
    @patch('app.services.Asset_service.Asset')
    def test_calcular_indicadores_carteira_no_bova11(self, mock_asset, mock_g):
        """Testa o erro quando BOVA11.SA não está na carteira."""
        
        # Setup mocks
        mock_g.current_user_id = 1
        
        # Create mock asset data without BOVA11.SA
        mock_assets = []
        tickers = ['ITUB4.SA', 'PETR4.SA']
        
        for i, ticker in enumerate(tickers):
            for j in range(5):
                asset = MagicMock()
                asset.ticker = ticker
                asset.date = date(2024, 1, j+1)
                asset.close = 30.0 + i + j * 0.5
                mock_assets.append(asset)
        
        mock_asset.get_assets_by_carteira_admin.return_value = mock_assets
        
        # Execute
        result, status_code = AssetService.calcular_indicadores_carteira(1)
        
        # Assertions
        self.assertEqual(status_code, 400)
        self.assertFalse(result['success'])
        self.assertIn('BOVA11.SA is required', result['message'])
    
    @patch('flask.g')
    @patch('app.services.Asset_service.Asset')
    def test_calcular_indicadores_carteira_no_data(self, mock_asset, mock_g):
        """Testa o erro quando não há dados na carteira."""
        
        # Setup mocks
        mock_g.current_user_id = 1
        mock_asset.get_assets_by_carteira_admin.return_value = []
        
        # Execute
        result, status_code = AssetService.calcular_indicadores_carteira(1)
        
        # Assertions
        self.assertEqual(status_code, 404)
        self.assertFalse(result['success'])
        self.assertIn('No assets found', result['message'])
    
    def test_calculate_index_asset_success(self):
        """Testa o cálculo de índices de um ativo."""
        
        # Create test DataFrame
        df = self.mock_df.copy()
        
        # Execute
        result = AssetService.calculateIndexAsset(df, "ITUB4.SA")
        
        # Assertions
        self.assertIn('results', result)
        self.assertIn('historico', result)
        
        if result['results']:  # Se há resultados válidos
            self.assertIn('retorno_esperado', result['results'])
            self.assertIn('desvio_padrao', result['results'])
            self.assertIn('indice_sharpe', result['results'])


class TestAssetServiceIntegration(unittest.TestCase):
    """Testes de integração para o AssetService."""
    
    def test_data_processing_pipeline(self):
        """Testa o pipeline completo de processamento de dados."""
        
        # Create realistic test data
        dates = pd.date_range('2024-01-01', periods=60, freq='D')
        prices = 30 + np.cumsum(np.random.randn(60) * 0.02)  # Random walk
        
        df = pd.DataFrame({
            'Close': prices,
            'Open': prices * 0.995,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Volume': np.random.randint(1000000, 5000000, 60)
        }, index=dates)
        
        # Test calculation
        result = AssetService.calculateIndexAsset(df, "TEST.SA")
        
        # Verify structure
        self.assertIn('results', result)
        self.assertIn('historico', result)
        
        # If results exist, verify they're numeric
        if result['results']:
            for key in ['retorno_esperado', 'desvio_padrao', 'indice_sharpe']:
                if key in result['results']:
                    self.assertIsInstance(result['results'][key], (int, float))


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    unittest.main(verbosity=2)
