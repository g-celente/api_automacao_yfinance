from flask import request, jsonify, current_app
from app.utils.middleware import request_logger, rate_limit, require_auth
from app.services.Asset_service import AssetService

class AssetController:
    """Controller for asset-related operations."""

    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests per minute
    def get_assets(self):
        """
        Retrieves a list of assets.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            data = request.get_json()
            ticker = data.get('asset_name', None)
            period = data.get('periodo', None)

            current_app.logger.info(f"Retrieving assets for ticker: {ticker}, period: {period}")

            if not ticker or not period:
                current_app.logger.warning("Ticker or Period is required to retrieve assets.")
                return jsonify({
                    "success": False,
                    "message": "Ticker and Period is required"
                }), 400
            
            response, status_code = AssetService.get_asset_data(ticker, period)

            if status_code != 200:
                current_app.logger.error(f"Failed to retrieve assets for ticker {ticker}: {response.get('message', 'Unknown error')}")
                return jsonify({
                    "success": False,
                    "message": response.get('message', 'Failed to retrieve assets')
                }), status_code

            current_app.logger.info("Assets retrieved successfully.")
            return {"success": True, "assets": response}, 200
        
        except Exception as e:
            current_app.logger.error(f"Error retrieving assets: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500

    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests per minute
    def add_asset(self):
        """
        Adds a new asset.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            data = request.get_json()
            current_app.logger.info(f"Adding asset with data: {data}")

            if not data or not data.get('ticker') or not data.get('period'):
                current_app.logger.warning("Ticker and Period are required to add an asset.")
                return jsonify({
                    "success": False,
                    "message": "Ticker and Period are required"
                }), 400
            
            response, status_code = AssetService.add_asset(data)

            if status_code != 201:
                current_app.logger.error(f"Failed to add asset: {response.get('message', 'Unknown error')}")
                return jsonify({
                    "success": False,
                    "message": response.get('message', 'Failed to add asset')
                }), status_code

            current_app.logger.info("Asset added successfully.")
            return jsonify({"success": True, "message": "Asset added successfully"}), 201
        
        except Exception as e:
            current_app.logger.error(f"Error adding asset: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500

    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests per minute
    def cadastrar_ativo(self):
        """
        Cadastra um novo ativo financeiro.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            data = request.get_json()
            current_app.logger.info(f"Cadastrando ativo com dados: {data}")

            if not data:
                current_app.logger.warning("Request body is required to add an asset.")
                return jsonify({
                    "success": False,
                    "message": "Request body with asset data is required"
                }), 400
            
            response, status_code = AssetService.cadastrar_ativo(data)

            if status_code != 201:
                current_app.logger.error(f"Falha ao cadastrar ativo: {response.get('message', 'Unknown error')}")
                return jsonify(response), status_code

            current_app.logger.info("Ativo cadastrado com sucesso.")
            return jsonify(response), 201
        
        except Exception as e:
            current_app.logger.error(f"Erro ao cadastrar ativo: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500

    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests per minute
    def get_indicadores_carteira(self, carteira_id):
        """
        Retorna indicadores financeiros de uma carteira.
        
        Args:
            carteira_id (int): ID da carteira
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            current_app.logger.info(f"Calculando indicadores para carteira {carteira_id}")

            if not carteira_id:
                current_app.logger.warning("Carteira ID is required.")
                return jsonify({
                    "success": False,
                    "message": "Carteira ID is required"
                }), 400
            
            response, status_code = AssetService.calcular_indicadores_carteira(carteira_id)

            if status_code != 200:
                current_app.logger.error(f"Falha ao calcular indicadores da carteira {carteira_id}: {response.get('message', 'Unknown error')}")
                return jsonify(response), status_code

            current_app.logger.info(f"Indicadores da carteira {carteira_id} calculados com sucesso.")
            return jsonify(response), 200
        
        except Exception as e:
            current_app.logger.error(f"Erro ao calcular indicadores: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500