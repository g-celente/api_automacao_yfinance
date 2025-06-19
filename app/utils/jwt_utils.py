# app/utils/jwt_utils.py
import jwt
import datetime
import os
from flask import current_app
import logging

logger = logging.getLogger(__name__)

# Fallback para desenvolvimento - em produção use variáveis de ambiente
DEFAULT_SECRET_KEY = "sua_chave_secreta_segura"

def get_secret_key():
    """
    Obtém a chave secreta do Flask config ou de variáveis de ambiente.
    
    Returns:
        str: Chave secreta para JWT
    """
    try:
        # Tenta pegar do Flask config primeiro
        if current_app:
            secret = current_app.config.get('SECRET_KEY')
            if secret:
                return secret
    except RuntimeError:
        # current_app não está disponível fora do contexto da aplicação
        pass
    
    # Fallback para variáveis de ambiente
    secret = os.getenv('SECRET_KEY') or os.getenv('JWT_SECRET_KEY')
    if secret:
        return secret
    
    # Último recurso - chave padrão (apenas para desenvolvimento)
    logger.warning("Usando chave secreta padrão. Configure SECRET_KEY em produção!")
    return DEFAULT_SECRET_KEY

def generate_token(user_id, role, expires_in=3600):
    """
    Gera um token JWT para o usuário.
    
    Args:
        user_id (int): ID do usuário
        role (str): Role/função do usuário (admin, user, etc.)
        expires_in (int): Tempo de expiração em segundos (padrão: 1 hora)
    
    Returns:
        str: Token JWT codificado
    """
    try:
        # Cria o payload do token
        payload = {
            'user_id': user_id,
            'role': role,
            'iat': datetime.datetime.utcnow(),  # Issued at
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        }
        
        # Codifica o token
        secret_key = get_secret_key()
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        logger.info(f"Token gerado para usuário {user_id} com role {role}")
        return token
        
    except Exception as e:
        logger.error(f"Erro ao gerar token para usuário {user_id}: {str(e)}")
        raise e

def decode_token(token):
    """
    Decodifica e valida um token JWT.
    
    Args:
        token (str): Token JWT para decodificar
    
    Returns:
        tuple: (payload, error_message)
               payload: Dados do token se válido, None se inválido
               error_message: Mensagem de erro se houver, None se válido
    """
    try:
        if not token or not isinstance(token, str):
            return None, "Token inválido"
        
        secret_key = get_secret_key()
        
        # Decodifica o token
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        # Validações adicionais
        if not payload.get('user_id'):
            return None, "Token sem identificação de usuário"
        
        if not payload.get('role'):
            return None, "Token sem role de usuário"
        
        logger.debug(f"Token decodificado com sucesso para usuário {payload.get('user_id')}")
        return payload, None
        
    except jwt.ExpiredSignatureError:
        logger.warning("Tentativa de uso de token expirado")
        return None, "Token expirado"
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token inválido: {str(e)}")
        return None, "Token inválido"
    except Exception as e:
        logger.error(f"Erro inesperado ao decodificar token: {str(e)}")
        return None, "Erro interno de autenticação"

def refresh_token(token, expires_in=3600):
    """
    Renova um token JWT existente.
    
    Args:
        token (str): Token atual
        expires_in (int): Novo tempo de expiração em segundos
    
    Returns:
        tuple: (new_token, error_message)
    """
    try:
        payload, error = decode_token(token)
        
        if error:
            return None, error
        
        # Gera um novo token com os mesmos dados
        new_token = generate_token(
            payload['user_id'], 
            payload['role'], 
            expires_in
        )
        
        logger.info(f"Token renovado para usuário {payload['user_id']}")
        return new_token, None
        
    except Exception as e:
        logger.error(f"Erro ao renovar token: {str(e)}")
        return None, "Erro ao renovar token"

def get_token_info(token):
    """
    Obtém informações do token sem validar expiração.
    
    Args:
        token (str): Token JWT
    
    Returns:
        dict: Informações do token ou None se inválido
    """
    try:
        secret_key = get_secret_key()
        
        # Decodifica sem verificar expiração
        payload = jwt.decode(
            token, 
            secret_key, 
            algorithms=['HS256'],
            options={"verify_exp": False}
        )
        
        return {
            'user_id': payload.get('user_id'),
            'role': payload.get('role'),
            'issued_at': payload.get('iat'),
            'expires_at': payload.get('exp'),
            'is_expired': datetime.datetime.utcnow().timestamp() > payload.get('exp', 0)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter informações do token: {str(e)}")
        return None
