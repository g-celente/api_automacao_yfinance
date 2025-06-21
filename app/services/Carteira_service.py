from app.model.Carteira import Carteira
from app.model.Cliente import Cliente
from flask import g

class CarteiraService:
    """Service for portfolio-related operations."""

    # ...existing code...
        
    @staticmethod
    def get_portfolios():
        """
        Retrieves all portfolios for the authenticated admin user.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            user_adm_id = g.current_user_id
            
            portfolios = Carteira.get_carteiras_by_admin(user_adm_id)
            if not portfolios:
                return {"success": False, "message": "No portfolios found"}, 404
            
            response = {
                "success": True,
                "portfolios": [portfolio.to_dict() for portfolio in portfolios]
            }
            return response, 200
        
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

    @staticmethod
    def update_portfolio(portfolio_id, data):
        """
        Updates a portfolio by ID, but only if it belongs to the authenticated admin's clients.
        
        Args:
            portfolio_id (int): ID of the portfolio to update.
            data (dict): Portfolio data to update.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            user_adm_id = g.current_user_id
            
            # Validação dos dados obrigatórios
            if not data.get('nome'):
                return {"success": False, "message": "Portfolio name is required"}, 400
            
            # Verifica se já existe uma carteira com o mesmo nome para o mesmo cliente
            # Primeiro busca a carteira atual para pegar o cliente_id
            carteira_atual = Carteira.query.join(Cliente).filter(
                Carteira.id == portfolio_id,
                Cliente.user_adm_id == user_adm_id
            ).first()
            
            if not carteira_atual:
                return {"success": False, "message": "Portfolio not found or not authorized"}, 404
            
            # Verifica se o novo nome já existe para o mesmo cliente (exceto a carteira atual)
            nome_existente = Carteira.query.filter(
                Carteira.nome == data.get('nome'),
                Carteira.cliente_id == carteira_atual.cliente_id,
                Carteira.id != portfolio_id
            ).first()
            
            if nome_existente:
                return {"success": False, "message": "Portfolio with this name already exists for this client"}, 409
            
            # Atualiza a carteira
            carteira_atualizada = Carteira.update_carteira_by_admin(portfolio_id, user_adm_id, data)
            
            if not carteira_atualizada:
                return {"success": False, "message": "Portfolio not found or not authorized"}, 404
            
            response = {
                "success": True,
                "message": "Portfolio updated successfully",
                "portfolio": carteira_atualizada.to_dict()
            }
            return response, 200
        
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

    @staticmethod 
    def get_portfolio_by_id(portfolio_id):
        """
        Retrieves a portfolio by ID, but only if it belongs to the authenticated admin's clients.
        
        Args:
            portfolio_id (int): ID of the portfolio to retrieve.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            user_adm_id = g.current_user_id
            
            # Busca a carteira e verifica se pertence a um cliente do admin
            carteira = Carteira.query.join(Cliente).filter(
                Carteira.id == portfolio_id,
                Cliente.user_adm_id == user_adm_id
            ).first()
            
            if not carteira:
                return {"success": False, "message": "Portfolio not found"}, 404
            
            response = {
                "success": True,
                "portfolio": carteira.to_dict()
            }
            return response, 200
        
        except Exception as e:
            return {"success": False, "message": str(e)}, 500
        
    @staticmethod
    def delete_portfolio(portfolio_id):
        """
        Deletes a portfolio by ID, but only if it belongs to the authenticated admin's clients.
        
        Args:
            portfolio_id (int): ID of the portfolio to delete.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            user_adm_id = g.current_user_id
            
            # Busca a carteira e verifica se pertence a um cliente do admin
            carteira = Carteira.query.join(Cliente).filter(
                Carteira.id == portfolio_id,
                Cliente.user_adm_id == user_adm_id
            ).first()
            
            if not carteira:
                return {"success": False, "message": "Portfolio not found"}, 404
            
            Carteira.delete(carteira)
            
            response = {
                "success": True,
                "message": "Portfolio deleted successfully"
            }
            return response, 200
        
        except Exception as e:
            return {"success": False, "message": str(e)}, 500

    @staticmethod
    def create_portfolio(data):
        """
        Creates a new portfolio for a client that belongs to the authenticated admin.
        
        Args:
            data (dict): Portfolio data.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            nome = data.get("nome")
            descricao = data.get("descricao")
            client_id = data.get("cliente_id")
            user_adm_id = g.current_user_id

            # Verifica se o cliente existe e pertence ao admin autenticado
            cliente = Cliente.query.filter_by(id=client_id, user_adm_id=user_adm_id).first()
            if not cliente:
                return {"success": False, "message": "Client not found or not authorized"}, 404
            
            carteira = Carteira(client_id, nome, descricao)
            Carteira.save(carteira)

            response = {
                "success": True,
                "message": "Portfolio created successfully",
                "portfolio": carteira.to_dict()
            }
            return response, 201
        
        except Exception as e:
            return {"success": False, "message": str(e)}, 500