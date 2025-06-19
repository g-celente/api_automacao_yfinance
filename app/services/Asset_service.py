import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional, List
import requests
from requests.exceptions import RequestException
import time
import os
import numpy as np

logger = logging.getLogger(__name__)

class AssetService:
    """Serviço para operações com ativos financeiros."""

    @classmethod
    def calculateIndexAsset(cls, df, asset: str):
        """
        Calcula dados de um Ativo Financeiro:
        - Retorno Esperado
        - Desvio Padrão
        - Sharpe Ratio
        
        Args:
            df: DataFrame com dados do ativo
            asset: Nome do ativo
            
        Returns:
            dict: Dicionário com os dados calculados do ativo.
        """
        try:
            # Trata MultiIndex nas colunas
            if isinstance(df.columns, pd.MultiIndex):
                # Achata o MultiIndex pegando apenas o primeiro nível para as colunas principais
                df.columns = df.columns.get_level_values(0)
            
            # Renomeia a coluna de fechamento
            if 'Close' in df.columns:
                df.rename(columns={'Close': 'fechamento'}, inplace=True)
            elif 'Adj Close' in df.columns:
                df.rename(columns={'Adj Close': 'fechamento'}, inplace=True)
            
            # Verifica se temos a coluna fechamento
            if 'fechamento' not in df.columns:
                logger.error(f"Coluna 'fechamento' não encontrada. Colunas disponíveis: {df.columns.tolist()}")
                return {
                    "results": {},
                    "historico": []
                }
            
            # Remove valores NaN
            df = df.dropna(subset=['fechamento'])
            
            if len(df) == 0:
                logger.warning("DataFrame vazio após remoção de NaN")
                return {
                    "results": {},
                    "historico": []
                }
            
            # Calcula variação percentual
            df['variacao'] = df['fechamento'].pct_change() * 100
            
            # Cálculos estatísticos
            retorno_esperado = df['variacao'].mean()
            desvio_padrao = df['variacao'].std()
            indice_sharpe = retorno_esperado / desvio_padrao if desvio_padrao != 0 else 0
            volatilidade_anual = desvio_padrao * np.sqrt(252)
            
            # Prepara dados históricos para o front-end
            df_clean = df.copy()
            df_clean.reset_index(inplace=True)
            
            # Trata diferentes nomes de coluna de data
            date_column = None
            for col in ['Date', 'Datetime', 'date', 'datetime']:
                if col in df_clean.columns:
                    date_column = col
                    break
            
            # Se não encontrou coluna de data, usa o índice original
            if date_column is None and hasattr(df.index, 'name') and df.index.name:
                date_column = df.index.name
            elif date_column is None:
                # Cria uma coluna de data baseada no índice
                df_clean['data'] = df.index
                date_column = 'data'
            
            # Converte dados para lista de dicionários de forma segura
            historico_list = []
            
            for idx, row in df_clean.iterrows():
                try:
                    # Extrai a data de forma segura
                    if date_column in df_clean.columns:
                        data_value = row[date_column]
                    else:
                        data_value = df.index[idx]
                    
                    # Converte para string de data limpa
                    if pd.isna(data_value):
                        continue
                        
                    # Se for Timestamp do pandas, converte para string
                    if hasattr(data_value, 'strftime'):
                        data_str = data_value.strftime('%Y-%m-%d')
                    elif isinstance(data_value, str):
                        # Se já for string, tenta extrair apenas a data
                        try:
                            data_parsed = pd.to_datetime(data_value)
                            data_str = data_parsed.strftime('%Y-%m-%d')
                        except:
                            data_str = str(data_value)[:10]  # Pega apenas os primeiros 10 caracteres
                    else:
                        # Tenta converter para datetime
                        try:
                            data_parsed = pd.to_datetime(str(data_value))
                            data_str = data_parsed.strftime('%Y-%m-%d')
                        except:
                            logger.warning(f"Não foi possível converter data: {data_value}")
                            continue
                    
                    # Extrai o preço de fechamento
                    fechamento_value = row['fechamento']
                    if pd.isna(fechamento_value):
                        continue
                    
                    historico_list.append({
                        'data': data_str,
                        'close': round(float(fechamento_value), 2),
                        'high': round(float(row.get('High', fechamento_value)), 2),
                        'low': round(float(row.get('Low', fechamento_value)), 2),
                        'open': round(float(row.get('Open', fechamento_value)), 2),
                    })
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar linha {idx}: {str(e)}")
                    continue
            
            
            return {
                "results": {
                    "retorno": round(float(retorno_esperado), 4),
                    "desvio": round(float(desvio_padrao), 4),
                    "volatilidadeAnual": round(float(volatilidade_anual), 4),
                    "sharpe": round(float(indice_sharpe), 4)
                },
                "historico": historico_list
            }
            
        except Exception as e:
            logger.error(f"Erro em calculateIndexAsset: {str(e)}")
            return {
                "results": {},
                "historico": []
            }


    @classmethod
    def get_asset_data(cls, asset: str, period: str = '1y', interval: str = '5d') -> Dict[str, Any]:
        """
            Busca informações de um ativo financeiro.        Args:
            asset: Símbolo do ativo (ex: PETR4, AAPL)
            start_date: Mercado (BR, US, CA) opcional, se fornecido, filtra os dados a partir dessa data.
            
        Returns:
            tuple: (response_data, status_code)
        """
        
        if not asset:
            return {"success": False, "message": "Asset symbol is required"}, 400
        
        try:
            if not asset.endswith('.SA'):
                asset = f"{asset}.SA"
        
            df = yf.download(asset, period=period, interval=interval)
            
            if df.empty:
                return {"success": False, "message": "No data found for the given asset"}, 404

            result = cls.calculateIndexAsset(df, asset)

            return result, 200
        
        except Exception as e:
            logger.error(f"Error fetching asset data: {str(e)}")
            return {"success": False, "message": str(e)}, 500