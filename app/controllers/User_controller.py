from flask import request, jsonify, current_app
from app.services.User_service import UserService
from app.utils.middleware import request_logger, rate_limit, require_auth
from marshmallow import Schema, fields, validate
import time
from flask import g

class UserSchema(Schema):
    """Schema para validação de dados do usuário."""
    name = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class UserController:
    """Controlador para operações relacionadas a usuários."""

    user_schema = UserSchema()

    @request_logger()
    @rate_limit(limit=5, window=60)  # Limite de 5 tentativas por minuto
    def register(self):
        """
        Registra um novo usuário.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            data = request.get_json()
            
            # Validação básica
            if not data or not data.get('email') or not data.get('password'):
                return jsonify({
                    "success": False,
                    "message": "Email e senha são obrigatórios"
                }), 400
            
            current_app.logger.info(f"Tentativa de registro para email: {data.get('email')}")
            response, status = UserService.register(data)
            
            if status == 201:
                current_app.logger.info(f"Usuário registrado com sucesso: {data.get('email')}")
            else:
                current_app.logger.warning(f"Falha no registro: {data.get('email')}")
            
            return jsonify(response), status
            
        except Exception as e:
            current_app.logger.error(f"Erro no registro: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Erro interno do servidor"
            }), 500

    @request_logger()
    @rate_limit(limit=5, window=60)  # Limite de 5 tentativas por minuto
    def login(self):
        """
        Autentica um usuário.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            data = request.get_json()
            
            # Validação básica
            if not data or not data.get('email') or not data.get('password'):
                return jsonify({
                    "success": False,
                    "message": "Email e senha são obrigatórios"
                }), 400
            
            current_app.logger.info(f"Tentativa de login para email: {data.get('email')}")
            response, status = UserService.login(data)
            
            if status == 200:
                current_app.logger.info(f"Login bem sucedido: {data.get('email')}")
            else:
                current_app.logger.warning(f"Falha no login: {data.get('email')}")
            
            return jsonify(response), status
            
        except Exception as e:
            current_app.logger.error(f"Erro no login: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Erro interno do servidor"
            }), 500

    @request_logger()
    @require_auth(['admin'])
    @rate_limit(limit=10, window=60)  # Limite de 10 requisições por minuto
    def get_user_by_id(self):
        """
        Obtém informações de um usuário pelo ID.
        
        Args:
            user_id (int): ID do usuário a ser buscado
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            user_id = g.current_user_id
            current_app.logger.info(f"Buscando usuário com ID: {user_id}")
            response, status = UserService.get_user_by_id(user_id)
            
            if status != 200:
                current_app.logger.warning(f"Usuário não encontrado: {user_id}")
                return jsonify(response), status
            
            current_app.logger.info(f"Usuário encontrado: {user_id}")
            return jsonify(response), 200
            
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar usuário: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Erro interno do servidor"
            }), 500

    @request_logger()
    @require_auth()
    def logout(self):
        """
        Realiza o logout do usuário invalidando o token atual.
        
        Returns:
            tuple: (response, status_code)
        """
        try:
            token = request.token
            token_payload = request.user
            
            # Calcula o tempo restante de validade do token
            expires_in = token_payload.get('exp', 0) - int(time.time())
            if expires_in <= 0:
                return jsonify({
                    "success": True,
                    "message": "Token já expirado"
                }), 200
            
            current_app.logger.info(f"Logout bem sucedido para usuário ID: {token_payload.get('user_id')}")
            return jsonify({
                "success": True,
                "message": "Logout realizado com sucesso"
            }), 200
                
        except Exception as e:
            current_app.logger.error(f"Erro no logout: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Erro interno do servidor"
            }), 500