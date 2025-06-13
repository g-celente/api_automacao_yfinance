from flask import request, jsonify, current_app
from app.services.User_service import UserService
from app.utils.middleware import request_logger, rate_limit
from marshmallow import Schema, fields, validate

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
            
            # Validação dos dados
            errors = self.user_schema.validate(data)
            if errors:
                return jsonify({"success": False, "errors": errors}), 400
            
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
