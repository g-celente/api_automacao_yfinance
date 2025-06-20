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

    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests
    def delete_client(self, cliente_id):
        """
        Deletes a client by ID.
        
        Args:
            cliente_id (int): ID of the client to delete
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            current_app.logger.info(f"Deleting client with ID: {cliente_id}")
            response, status = ClienteService.deleteUser(cliente_id)
            
            if status != 200:
                current_app.logger.warning(f"Failed to delete client: {response.get('message')}")
                return jsonify(response), 400
            
            current_app.logger.info("Client deleted successfully.")
            return jsonify(response), 200
        
        except Exception as e:
            current_app.logger.error(f"Error deleting client: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500
        
    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests
    def update_client(self, cliente_id):
        """
        Updates a client by ID.
        
        Args:
            cliente_id (int): ID of the client to update
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            data = request.get_json()
            current_app.logger.info(f"Updating client with ID: {cliente_id} and data: {data}")
            response, status = ClienteService.update_cliente(cliente_id, data)
            
            if status != 200:
                current_app.logger.warning(f"Failed to update client: {response.get('message')}")
                return jsonify(response), 400
            
            current_app.logger.info("Client updated successfully.")
            return jsonify(response), 200
        
        except Exception as e:
            current_app.logger.error(f"Error updating client: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500
        
    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limit to 10 requests
    def get_client_by_id(self, cliente_id):
        """
        Retrieves a client by ID.
        
        Args:
            cliente_id (int): ID of the client to retrieve
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            current_app.logger.info(f"Retrieving client with ID: {cliente_id}")
            response, status = ClienteService.get_cliente_by_id(cliente_id)
            
            if status != 200:
                current_app.logger.warning(f"Failed to retrieve client: {response.get('message')}")
                return jsonify(response), 400
            
            current_app.logger.info("Client retrieved successfully.")
            return jsonify(response), 200
        
        except Exception as e:
            current_app.logger.error(f"Error retrieving client: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500