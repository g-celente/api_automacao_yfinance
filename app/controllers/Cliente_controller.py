from flask import request, jsonify, current_app
from app.utils.middleware import request_logger, rate_limit, require_auth
from app.services.Cliente_service import ClienteService

class ClienteController:
    """Controller for client-related operations."""

    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests per minute
    def create_client(self):
        """
        Creates a new client.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            data = request.get_json()
            current_app.logger.info(f"Creating client with data: {data}")

            # Simulating a successful creation for demonstration purposes
            response, status = ClienteService.create_cliente(data)
            if status != 201:
                current_app.logger.warning(f"Failed to create client: {response.get('message')}")
                return jsonify(response), 400

            status_code = 201

            current_app.logger.info("Client created successfully.")
            return jsonify(response), status_code
        
        except Exception as e:
            current_app.logger.error(f"Error creating client: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500
        
    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests
    def get_clients(self):
        """
        Retrieves a list of clients.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            current_app.logger.info("Retrieving clients.")
            response, status = ClienteService.get_clientes()
            
            if status != 200:
                current_app.logger.warning(f"Failed to retrieve clients: {response.get('message')}")
                return jsonify(response), 400
            
            current_app.logger.info("Clients retrieved successfully.")
            return jsonify(response), 200
        
        except Exception as e:
            current_app.logger.error(f"Error retrieving clients: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500