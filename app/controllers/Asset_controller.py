from flask import request, jsonify, current_app
from app.utils.middleware import request_logger, rate_limit, require_auth
from app.services.Asset_service import AssetService

class AssetController:
    """Controller for asset-related operations."""

    @request_logger()
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