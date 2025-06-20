from mvc_flask import Router
from flask import jsonify


# Health check route
Router.get('/api/health', 'Health#get_health')

# Rotas para Usuários Administrativos
Router.post('/api/login', 'User#login')
Router.post('/api/register', 'User#register')
Router.post('/api/logout', 'User#logout')

#Rotas para Clientes do Usuário Administrativo
Router.post('/api/clients', 'Cliente#create_client')
Router.get('/api/clients', 'Cliente#get_clients')
Router.delete('/api/clients/<int:cliente_id>', 'Cliente#delete_client')
Router.put('/api/clients/<int:cliente_id>', 'Cliente#update_client')
Router.get('/api/clients/<int:cliente_id>', 'Cliente#get_client_by_id')

# Rotas para Ativos
Router.post('/api/assets/search', 'Asset#get_assets')

