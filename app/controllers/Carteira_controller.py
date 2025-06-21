from flask import request, jsonify, current_app
from app.utils.middleware import request_logger, rate_limit, require_auth
from app.services.Carteira_service import CarteiraService

class CarteiraController:
    """Controller for portfolio-related operations."""

    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests per minute
    def create_portfolio(self):
        """
        Creates a new portfolio.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            data = request.get_json()
            current_app.logger.info(f"Creating portfolio with data: {data}")

            # Simulating a successful creation for demonstration purposes
            response, status = CarteiraService.create_portfolio(data)
            if status != 201:
                current_app.logger.warning(f"Failed to create portfolio: {response.get('message')}")
                return jsonify(response), 400

            status_code = 201

            current_app.logger.info("Portfolio created successfully.")
            return jsonify(response), status_code
        
        except Exception as e:
            current_app.logger.error(f"Error creating portfolio: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500
    
    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests per minute
    def get_portfolio_by_id(self, portfolio_id):
        """
        Retrieves a portfolio by Id.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            current_app.logger.info(f"Retrieving portfolio with ID: {portfolio_id}")

            if not portfolio_id:
                current_app.logger.warning("Portfolio ID is required to retrieve a portfolio.")
                return jsonify({
                    "success": False,
                    "message": "Portfolio ID is required"
                }), 400
            
            response, status_code = CarteiraService.get_portfolio_by_id(portfolio_id)

            if status_code != 200:
                current_app.logger.error(f"Failed to retrieve portfolio with ID {portfolio_id}: {response.get('message', 'Unknown error')}")
                return jsonify({
                    "success": False,
                    "message": response.get('message', 'Failed to retrieve portfolio')
                }), status_code

            current_app.logger.info("Portfolio retrieved successfully.")
            return jsonify(response), 200
        
        except Exception as e:
            current_app.logger.error(f"Error retrieving portfolio: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500
        
    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests per minute
    def get_portfolios(self):
        """
        Retrieves a list of portfolios.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            current_app.logger.info("Retrieving portfolios.")
            response, status = CarteiraService.get_portfolios()
            
            if status != 200:
                current_app.logger.warning(f"Failed to retrieve portfolios: {response.get('message')}")
                return jsonify(response), 400
            
            current_app.logger.info("Portfolios retrieved successfully.")
            return jsonify(response), 200
        
        except Exception as e:
            current_app.logger.error(f"Error retrieving portfolios: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500

    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests per minute
    def update_portfolio(self, portfolio_id):
        """
        Updates a portfolio by ID.
        
        Args:
            portfolio_id (int): ID of the portfolio to update
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            data = request.get_json()
            current_app.logger.info(f"Updating portfolio {portfolio_id} with data: {data}")

            if not portfolio_id:
                current_app.logger.warning("Portfolio ID is required to update a portfolio.")
                return jsonify({
                    "success": False,
                    "message": "Portfolio ID is required"
                }), 400
            
            if not data:
                current_app.logger.warning("Request body is required to update a portfolio.")
                return jsonify({
                    "success": False,
                    "message": "Request body with portfolio data is required"
                }), 400
            
            response, status_code = CarteiraService.update_portfolio(portfolio_id, data)

            if status_code != 200:
                current_app.logger.error(f"Failed to update portfolio with ID {portfolio_id}: {response.get('message', 'Unknown error')}")
                return jsonify(response), status_code

            current_app.logger.info(f"Portfolio {portfolio_id} updated successfully.")
            return jsonify(response), 200
        
        except Exception as e:
            current_app.logger.error(f"Error updating portfolio: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500
        
    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests per minute
    def delete_portfolio(self, portfolio_id):
        """
        Deletes a portfolio by Id.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            current_app.logger.info(f"Deleting portfolio with ID: {portfolio_id}")

            if not portfolio_id:
                current_app.logger.warning("Portfolio ID is required to delete a portfolio.")
                return jsonify({
                    "success": False,
                    "message": "Portfolio ID is required"
                }), 400
            
            response, status_code = CarteiraService.delete_portfolio(portfolio_id)

            if status_code != 200:
                current_app.logger.error(f"Failed to delete portfolio with ID {portfolio_id}: {response.get('message', 'Unknown error')}")
                return jsonify({
                    "success": False,
                    "message": response.get('message', 'Failed to delete portfolio')
                }), status_code

            current_app.logger.info("Portfolio deleted successfully.")
            return jsonify(response), 200
        
        except Exception as e:
            current_app.logger.error(f"Error deleting portfolio: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500