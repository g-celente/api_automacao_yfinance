from functools import wraps
from flask import request, jsonify, current_app
from app.utils.jwt_utils import decode_token
import time

def require_auth(roles=None):
    """
    Decorator para proteger rotas que requerem autenticação.
    
    Args:
        roles (list, optional): Lista de roles permitidos. Defaults to None.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({'message': 'Token não fornecido'}), 401
            
            try:
                token = auth_header.split(' ')[1]
                
                payload, error = decode_token(token)
                
                if error:
                    return jsonify({'message': error}), 401
                
                if roles and payload.get('role') not in roles:
                    return jsonify({'message': 'Acesso não autorizado'}), 403
                
                # Adiciona informações do usuário e token ao request
                request.user = payload
                request.token = token
                return f(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f'Erro de autenticação: {str(e)}')
                return jsonify({'message': 'Erro de autenticação'}), 401
        
        return decorated
    return decorator

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