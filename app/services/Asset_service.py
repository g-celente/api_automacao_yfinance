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

    @staticmethod
    def cadastrar_ativo(data: Dict[str, Any]) -> tuple:
        """
        Cadastra um novo ativo financeiro buscando dados do yfinance.
        
        Args:
            data: Dicionário com ticker, carteira_id, intervalo, period
            
        Returns:
            tuple: (response_dict, status_code)
        """
        try:
            from flask import g
            from app.model.Asset import Asset
            from app.model.Carteira import Carteira
            from app.model.Cliente import Cliente
            from app import db
            
            user_adm_id = g.current_user_id
            ticker = data.get('ticker', '').upper()
            carteira_id = data.get('carteira_id')
            intervalo = data.get('intervalo', '1d')
            period = data.get('period', '3mo')  # 3 meses = ~90 dias
            
            # Validações
            if not ticker:
                return {"success": False, "message": "Ticker is required"}, 400
            
            if not ticker.endswith('.SA'):
                ticker = f"{ticker}.SA"
            
            if not carteira_id:
                return {"success": False, "message": "Carteira ID is required"}, 400
            
            # Verifica se a carteira existe e pertence ao admin
            carteira = Carteira.query.join(Cliente).filter(
                Carteira.id == carteira_id,
                Cliente.user_adm_id == user_adm_id
            ).first()
            
            if not carteira:
                return {"success": False, "message": "Carteira not found or not authorized"}, 404
            
            # Busca dados do yfinance
            logger.info(f"Buscando dados do ticker {ticker} para período {period}")
            
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=period, interval=intervalo)
                
                if hist.empty:
                    return {"success": False, "message": f"No data found for ticker {ticker}"}, 404
                
            except Exception as yf_error:
                logger.error(f"Erro ao buscar dados do yfinance: {yf_error}")
                return {"success": False, "message": f"Error fetching data from yfinance: {str(yf_error)}"}, 500
            
            # Prepara dados para inserção
            assets_to_insert = []
            existing_count = 0
            
            for date, row in hist.iterrows():
                # Converte timestamp para date
                date_only = date.date()
                
                # Verifica se já existe
                existing_asset = Asset.query.filter_by(
                    carteira_id=carteira_id,
                    ticker=ticker,
                    date=date_only
                ).first()
                
                if existing_asset:
                    existing_count += 1
                    continue
                
                # Cria novo asset
                new_asset = Asset(
                    carteira_id=carteira_id,
                    ticker=ticker,
                    date=date_only,
                    close=float(row['Close'])
                )
                assets_to_insert.append(new_asset)
            
            # Inserção em lote
            inserted_count = 0
            if assets_to_insert:
                try:
                    db.session.bulk_save_objects(assets_to_insert)
                    db.session.commit()
                    inserted_count = len(assets_to_insert)
                except Exception as db_error:
                    db.session.rollback()
                    logger.error(f"Erro ao inserir no banco: {db_error}")
                    return {"success": False, "message": f"Database error: {str(db_error)}"}, 500
            
            return {
                "success": True,
                "message": f"Asset {ticker} processed successfully",
                "data": {
                    "ticker": ticker,
                    "carteira_id": carteira_id,
                    "total_records": len(hist),
                    "inserted_records": inserted_count,
                    "existing_records": existing_count,
                    "period": period,
                    "intervalo": intervalo
                }
            }, 201
            
        except Exception as e:
            logger.error(f"Erro ao cadastrar ativo: {str(e)}")
            return {"success": False, "message": f"Internal server error: {str(e)}"}, 500

    @staticmethod
    def calcular_indicadores_carteira(carteira_id: int) -> tuple:
        """
        Calcula indicadores financeiros para uma carteira.
        
        Args:
            carteira_id: ID da carteira
            
        Returns:
            tuple: (response_dict, status_code)
        """
        try:
            from flask import g
            from app.model.Asset import Asset
            from app.model.Carteira import Carteira
            from app.model.Cliente import Cliente
            
            user_adm_id = g.current_user_id
            
            # Verifica se a carteira existe e pertence ao admin
            carteira = Carteira.query.join(Cliente).filter(
                Carteira.id == carteira_id,
                Cliente.user_adm_id == user_adm_id
            ).first()
            
            if not carteira:
                return {"success": False, "message": "Carteira not found or not authorized"}, 404
            
            # Busca todos os ativos da carteira
            assets = Asset.query.filter_by(carteira_id=carteira_id).all()
            
            if not assets:
                return {"success": False, "message": "No assets found in this carteira"}, 200
            
            # Converte para DataFrame
            df_data = []
            for asset in assets:
                df_data.append({
                    'ticker': asset.ticker,
                    'date': asset.date,
                    'close': asset.close
                })
            
            df = pd.DataFrame(df_data)
            
            # Pivot para ter tickers como colunas
            df_pivot = df.pivot_table(index='date', columns='ticker', values='close', aggfunc='first')
            df_pivot = df_pivot.dropna()
            
            if df_pivot.empty:
                return {"success": False, "message": "Insufficient data for calculations"}, 400
            
            # Verifica se BOVA11.SA existe
            if 'BOVA11.SA' not in df_pivot.columns:
                return {"success": False, "message": "BOVA11.SA is required for calculations"}, 400
            
            # Calcula retornos diários
            returns = df_pivot.pct_change().dropna()
            
            # Ordena tickers com BOVA11.SA no final
            tickers = list(df_pivot.columns)
            if 'BOVA11.SA' in tickers:
                tickers.remove('BOVA11.SA')
                tickers.append('BOVA11.SA')
            
            # Calcula indicadores
            retorno_esperado = returns.mean()
            desvio_padrao = returns.std()
            
            # Índice de desempenho (Sharpe simples)
            indice_desempenho = retorno_esperado / desvio_padrao
            
            # Índice de Sharpe (assumindo taxa livre de risco = 0.5% ao ano / 252 dias úteis)
            taxa_livre_risco = 0.005 / 252
            indice_sharpe = (retorno_esperado - taxa_livre_risco) / desvio_padrao
            
            # Pesos igualitários (excluindo BOVA11.SA)
            ativos_investimento = [t for t in tickers if t != 'BOVA11.SA']
            n_ativos = len(ativos_investimento)
            
            if n_ativos == 0:
                return {"success": False, "message": "No investment assets found (excluding BOVA11.SA)"}, 400
            
            peso_individual = 1.0 / n_ativos
            pesos = pd.Series(index=tickers, data=0.0)
            for ticker in ativos_investimento:
                pesos[ticker] = peso_individual
            
            # Retorno da carteira
            retorno_carteira = np.dot(retorno_esperado[ativos_investimento], pesos[ativos_investimento])
            
            # Cálculo do Beta
            bova_returns = returns['BOVA11.SA']
            bova_variance = bova_returns.var()
            
            beta = {}
            for ticker in tickers:
                if ticker != 'BOVA11.SA':
                    covariance = returns[ticker].cov(bova_returns)
                    beta[ticker] = covariance / bova_variance if bova_variance != 0 else 0
                else:
                    beta[ticker] = 1.0
            
            # Matriz de covariância
            matriz_covariancia = returns.cov()
            
            # Matriz de covariância customizada baseada no Beta
            matriz_cov_customizada = pd.DataFrame(index=tickers, columns=tickers)
            for i, ticker_i in enumerate(tickers):
                for j, ticker_j in enumerate(tickers):
                    if ticker_i == ticker_j:
                        matriz_cov_customizada.loc[ticker_i, ticker_j] = returns[ticker_i].var()
                    else:
                        # Cov(i,j) = Beta_i * Beta_j * Var(mercado)
                        cov_custom = beta[ticker_i] * beta[ticker_j] * bova_variance
                        matriz_cov_customizada.loc[ticker_i, ticker_j] = cov_custom
            
            matriz_cov_customizada = matriz_cov_customizada.astype(float)
            
            # Desvio padrão da carteira
            pesos_array = pesos[ativos_investimento].values
            cov_matrix = matriz_covariancia.loc[ativos_investimento, ativos_investimento].values
            variancia_carteira = np.dot(pesos_array, np.dot(cov_matrix, pesos_array))
            desvio_padrao_carteira = np.sqrt(variancia_carteira)
            
            # Indicadores finais da carteira
            indice_desempenho_carteira = retorno_carteira / desvio_padrao_carteira if desvio_padrao_carteira != 0 else 0
            indice_sharpe_carteira = (retorno_carteira - taxa_livre_risco) / desvio_padrao_carteira if desvio_padrao_carteira != 0 else 0
            
            # Monta resposta
            response = {
                "success": True,
                "carteira_id": carteira_id,
                "indicadores": {
                    "ativos_ordenados": tickers,
                    "retorno_esperado": {ticker: float(retorno_esperado[ticker]) for ticker in tickers},
                    "desvio_padrao": {ticker: float(desvio_padrao[ticker]) for ticker in tickers},
                    "indice_desempenho": {ticker: float(indice_desempenho[ticker]) if not pd.isna(indice_desempenho[ticker]) else 0.0 for ticker in tickers},
                    "indice_sharpe": {ticker: float(indice_sharpe[ticker]) if not pd.isna(indice_sharpe[ticker]) else 0.0 for ticker in tickers},
                    "pesos": {ticker: float(pesos[ticker]) for ticker in tickers},
                    "retorno_carteira": float(retorno_carteira),
                    "beta": {ticker: float(beta[ticker]) for ticker in tickers},
                    "matriz_covariancia": {col: {row: float(matriz_covariancia.loc[row, col]) for row in matriz_covariancia.index} for col in matriz_covariancia.columns},
                    "matriz_cov_customizada": {col: {row: float(matriz_cov_customizada.loc[row, col]) for row in matriz_cov_customizada.index} for col in matriz_cov_customizada.columns},
                    "desvio_padrao_carteira": float(desvio_padrao_carteira),
                    "indicadores_carteira": {
                        "retorno_esperado": float(retorno_carteira),
                        "variancia": float(variancia_carteira),
                        "desvio_padrao": float(desvio_padrao_carteira),
                        "indice_desempenho": float(indice_desempenho_carteira),
                        "indice_sharpe": float(indice_sharpe_carteira)
                    }
                }
            }
            
            return response, 200
            
        except Exception as e:
            logger.error(f"Erro ao calcular indicadores: {str(e)}")
            return {"success": False, "message": f"Internal server error: {str(e)}"}, 500