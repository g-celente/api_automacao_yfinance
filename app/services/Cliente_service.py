from app.model.Cliente import Cliente
from flask import g

class ClienteService:

    @staticmethod
    def create_cliente(data):
        nome = data.get("nome")
        email = data.get("email")
        telefone = data.get("telefone")
        cpf = data.get("cpf")
        status = 'active' # Default status is 'ativo'
        user_adm_id = g.current_user_id

        if not all([nome, email, telefone, cpf, status]):
            return {"success": False, "message": "Todos os campos são obrigatórios."}, 400
        
        if Cliente.find_by_cpf(cpf):
            return {"success": False, "message": "CPF já está em uso."}, 400

        cliente = Cliente(name=nome, email=email, telefone=telefone, cpf=cpf, status=status, user_adm_id=user_adm_id)
        Cliente.save(cliente)

        return {"success": True, "message": "Cliente criado com sucesso."}, 201

    @staticmethod
    def get_clientes():
        
        user_adm_id = g.current_user_id

        clientes = Cliente.get_clientes_by_admin(user_adm_id)
        if not clientes:
            return {"success": False, "message": "Nenhum cliente encontrado."}, 404
    
        return {"success": True, "clientes": [cliente.to_dict() for cliente in clientes]}, 200