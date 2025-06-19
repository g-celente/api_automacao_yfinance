# Exemplo de uso do middleware @require_auth em controllers

from flask import request, jsonify, current_app, g
from app.services.User_service import UserService
from app.utils.middleware import require_auth, require_admin, require_user, request_logger, rate_limit

class ExampleController:
    """Exemplos de como usar o middleware de autenticação."""
    
    @request_logger()
    @rate_limit(limit=5, window=60)
    def login(self):
        """
        Rota pública de login - não precisa de autenticação.
        """
        try:
            data = request.get_json()
            response, status = UserService.login(data)
            return jsonify(response), status
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @request_logger()
    @require_user()  # Qualquer usuário autenticado pode acessar
    def get_profile(self):
        """
        Obtém o perfil do usuário autenticado.
        O usuário já está disponível em g.current_user
        """
        try:
            user_data = g.current_user
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user_data['id'],
                    'name': user_data['name'],
                    'email': user_data['email'],
                    'role': user_data['role']
                }
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Erro ao obter perfil: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Erro interno do servidor'
            }), 500
    
    @request_logger()
    @require_user()  # Qualquer usuário autenticado
    def update_profile(self):
        """
        Atualiza o perfil do usuário autenticado.
        """
        try:
            user_id = g.current_user_id
            data = request.get_json()
            
            # Código para atualizar perfil...
            response, status = UserService.update_user(user_id, data)
            return jsonify(response), status
            
        except Exception as e:
            current_app.logger.error(f"Erro ao atualizar perfil: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Erro interno do servidor'
            }), 500
    
    @request_logger()
    @require_admin()  # Apenas administradores
    def get_all_users(self):
        """
        Lista todos os usuários - apenas para administradores.
        """
        try:
            current_app.logger.info(f"Admin {g.current_user_id} solicitou lista de usuários")
            
            users = UserService.get_all_users()
            return jsonify({
                'success': True,
                'users': users,
                'requested_by': g.current_user['name']
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Erro ao listar usuários: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Erro interno do servidor'
            }), 500
    
    @request_logger()
    @require_auth(['admin', 'moderator'])  # Admin ou moderador
    def moderate_content(self):
        """
        Modera conteúdo - apenas admin ou moderador.
        """
        try:
            current_app.logger.info(f"Usuário {g.current_user_id} ({g.current_user_role}) acessou moderação")
            
            return jsonify({
                'success': True,
                'message': 'Acesso autorizado à moderação',
                'user_role': g.current_user_role
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Erro na moderação: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Erro interno do servidor'
            }), 500
    
    @request_logger()
    @require_auth(['admin'])  # Forma alternativa de especificar apenas admin
    def admin_dashboard(self):
        """
        Dashboard administrativo.
        """
        try:
            return jsonify({
                'success': True,
                'message': f'Bem-vindo ao painel admin, {g.current_user["name"]}!',
                'admin_data': {
                    'total_users': 150,
                    'active_sessions': 25,
                    'server_status': 'online'
                }
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Erro no dashboard admin: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Erro interno do servidor'
            }), 500


# Como registrar as rotas
"""
from flask import Blueprint
from app.controllers.example_controller import ExampleController

api = Blueprint('api', __name__)
controller = ExampleController()

# Rotas públicas
api.add_url_rule('/login', 'login', controller.login, methods=['POST'])

# Rotas protegidas (usuário autenticado)
api.add_url_rule('/profile', 'get_profile', controller.get_profile, methods=['GET'])
api.add_url_rule('/profile', 'update_profile', controller.update_profile, methods=['PUT'])

# Rotas administrativas
api.add_url_rule('/admin/users', 'get_all_users', controller.get_all_users, methods=['GET'])
api.add_url_rule('/admin/dashboard', 'admin_dashboard', controller.admin_dashboard, methods=['GET'])

# Rotas de moderação
api.add_url_rule('/moderate', 'moderate_content', controller.moderate_content, methods=['POST'])
"""
