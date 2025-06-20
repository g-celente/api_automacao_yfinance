from app.model.User import User
from app.utils.jwt_utils import generate_token

class UserService:

    @staticmethod
    def register(data):
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = 'admin'

        if not all([name, email, password]):
            return {"success": False, "message": "Todos os campos são obrigatórios."}, 400

        if User.find_by_email(email):
            return {"success": False, "message": "Email já está em uso."}, 400


        User.add_user_adm(name, email, password, role)

        return {"success": True, "message": "Usuário registrado com sucesso."}, 201

    @staticmethod
    def login(data):
        email = data.get("email")
        password = data.get("password")

        if not all([email, password]):
            return {"success": False, "message": "Email e senha são obrigatórios."}, 400

        user = User.find_by_email(email)
        if not user or not user.check_password(password):
            return {"success": False, "message": "Credenciais inválidas."}, 401

        token = generate_token(user.id, user.role)

        return {
            "success": True,
            "message": "Login realizado com sucesso.",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }, 200
    
    def get_user_by_id(user_id):
        """
        Busca um usuário pelo ID.
        
        Args:
            user_id (int): ID do usuário
        
        Returns:
            tuple: (response, status_code)
        """
        user = User.query.get(user_id)
        
        if not user:
            return {"success": False, "message": "Usuário não encontrado."}, 404
        
        return {
            "success": True,
            "user": user.to_dict()
        }, 200

    