from functools import wraps
from flask import request, jsonify, current_app, g
from app.utils.jwt_utils import decode_token
import time
import logging

logger = logging.getLogger(__name__)

def require_auth(roles=None):
    """
    Decorator para proteger rotas que requerem autenticação JWT.
    
    Args:
        roles (list, optional): Lista de roles permitidos (ex: ['admin', 'user']). 
                               Se None, qualquer usuário autenticado pode acessar.
    
    Usage:
        @require_auth()  # Qualquer usuário autenticado
        @require_auth(['admin'])  # Apenas administradores
        @require_auth(['admin', 'moderator'])  # Admin ou moderador
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # 1. Verifica se o header Authorization está presente
                auth_header = request.headers.get('Authorization')
                
                if not auth_header:
                    logger.warning(f"Tentativa de acesso sem token na rota {request.path}")
                    return jsonify({
                        'success': False,
                        'message': 'Token de autorização é obrigatório'
                    }), 401
                
                # 2. Extrai o token do header (formato: "Bearer <token>")
                try:
                    parts = auth_header.split(' ')
                    
                    if len(parts) != 2 or parts[0].lower() != 'bearer':
                        logger.warning(f"Formato de token inválido na rota {request.path}")
                        return jsonify({
                            'success': False,
                            'message': 'Formato do token inválido. Use: Bearer <token>'
                        }), 401
                    
                    token = parts[1]
                    
                    if not token or token.strip() == '':
                        logger.warning(f"Token vazio na rota {request.path}")
                        return jsonify({
                            'success': False,
                            'message': 'Token não pode estar vazio'
                        }), 401
                        
                except Exception as e:
                    logger.warning(f"Erro ao processar header Authorization: {str(e)}")
                    return jsonify({
                        'success': False,
                        'message': 'Formato do header Authorization inválido'
                    }), 401
                
                # 3. Valida o token JWT usando jwt_utils
                payload, error = decode_token(token)
                
                if error:
                    logger.warning(f"Token inválido na rota {request.path}: {error}")
                    return jsonify({
                        'success': False,
                        'message': error
                    }), 401
                
                if not payload:
                    logger.warning(f"Payload vazio na rota {request.path}")
                    return jsonify({
                        'success': False,
                        'message': 'Token inválido'
                    }), 401
                
                # 4. Extrai dados do usuário do payload
                user_id = payload.get('user_id')
                user_role = payload.get('role')
                
                if not user_id:
                    logger.warning(f"Token sem user_id na rota {request.path}")
                    return jsonify({
                        'success': False,
                        'message': 'Token inválido: usuário não identificado'
                    }), 401
                
                # 5. Verifica se o usuário tem permissão (role)
                if roles and user_role not in roles:
                    logger.warning(f"Acesso negado para usuário {user_id} com role {user_role} na rota {request.path}")
                    return jsonify({
                        'success': False,
                        'message': f'Acesso não autorizado. Roles permitidos: {", ".join(roles)}'
                    }), 403
                
                # 6. Verifica se o usuário existe no banco de dados (opcional)
                try:
                    from app.model.User import User
                    user = User.query.filter_by(id=user_id).first()
                    
                    if not user:
                        logger.warning(f"Usuário {user_id} não encontrado no banco de dados")
                        return jsonify({
                            'success': False,
                            'message': 'Usuário não encontrado'
                        }), 401
                        
                    # Verifica se o usuário está ativo (se o campo existir)
                    if hasattr(user, 'active') and not user.active:
                        logger.warning(f"Usuário {user_id} está inativo")
                        return jsonify({
                            'success': False,
                            'message': 'Usuário inativo'
                        }), 401
                    
                    # 7. Adiciona informações do usuário ao contexto da request
                    g.current_user_id = user_id
                    g.current_user_role = user_role
                    g.current_user = {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'role': user_role
                    }
                    g.token_payload = payload
                    
                    # Também mantém compatibilidade com o código existente
                    request.user = payload
                    request.token = token
                    
                except ImportError:
                    # Se não conseguir importar o modelo User, usa apenas os dados do token
                    logger.debug("Modelo User não disponível, usando apenas dados do token")
                    g.current_user_id = user_id
                    g.current_user_role = user_role
                    g.current_user = payload
                    g.token_payload = payload
                    request.user = payload
                    request.token = token
                
                except Exception as e:
                    logger.error(f"Erro ao verificar usuário no banco: {str(e)}")
                    return jsonify({
                        'success': False,
                        'message': 'Erro interno de autenticação'
                    }), 500
                
                logger.info(f"Autenticação bem-sucedida para usuário {user_id} na rota {request.path}")
                
                # 8. Prossegue com a execução da função original
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Erro inesperado na autenticação: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Erro interno de autenticação'
                }), 500
        
        return decorated
    return decorator


def require_admin():
    """
    Decorator que verifica se o usuário é administrador.
    É um atalho para @require_auth(['admin']).
    
    Usage:
        @require_admin()
        def admin_only_route():
            pass
    """
    return require_auth(['admin'])


def require_user():
    """
    Decorator que verifica autenticação básica (qualquer usuário válido).
    É um atalho para @require_auth().
    
    Usage:
        @require_user()
        def user_route():
            pass
    """
    return require_auth()

def request_logger():
    """Middleware para logging de requests."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            start_time = time.time()
            
            # Log da request
            current_app.logger.info({
                'method': request.method,
                'path': request.path,
                'ip': request.remote_addr,
                'user_agent': request.user_agent.string,
                'user_id': getattr(request, 'user', {}).get('user_id', None)
            })
            
            response = f(*args, **kwargs)
            print(response)
            
            # Log da response
            duration = round((time.time() - start_time) * 1000, 2)
            current_app.logger.info({
                'path': request.path,
                'duration_ms': duration,
                'status': response[1] if isinstance(response, tuple) else response.status_code,
            })
            
            return response
        return decorated
    return decorator

def rate_limit(limit=100, window=60):
    """
    Implementa rate limiting básico por IP.
    
    Args:
        limit (int): Número máximo de requests
        window (int): Janela de tempo em segundos
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # TODO: Implementar com Redis para produção
            return f(*args, **kwargs)
        return decorated
    return decorator

