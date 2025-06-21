from mvc_flask import Router
from flask import jsonify


# Health check route
Router.get('/api/health', 'Health#get_health')

# Rotas para Usuários Administrativos
Router.post('/api/login', 'User#login')
Router.post('/api/register', 'User#register')
Router.post('/api/logout', 'User#logout')
Router.get('/api/users', 'User#get_user_by_id')

#Rotas para Clientes do Usuário Administrativo
Router.post('/api/clients', 'Cliente#create_client')
Router.get('/api/clients', 'Cliente#get_clients')
Router.delete('/api/clients/<int:cliente_id>', 'Cliente#delete_client')
Router.put('/api/clients/<int:cliente_id>', 'Cliente#update_client')
Router.get('/api/clients/<int:cliente_id>', 'Cliente#get_client_by_id')

#Rotas para Carteiras do Usuário Administrativo
Router.post('/api/wallets', 'Carteira#create_portfolio')
Router.get('/api/wallets', 'Carteira#get_portfolios')
Router.put('/api/wallets/<int:portfolio_id>', 'Carteira#update_portfolio')
Router.delete('/api/wallets/<int:portfolio_id>', 'Carteira#delete_portfolio')
Router.get('/api/wallets/<int:portfolio_id>', 'Carteira#get_portfolio_by_id')
Router.get('/api/wallets/<int:carteira_id>/indicadores', 'Asset#get_indicadores_carteira')

# Rotas para Ativos
Router.post('/api/assets/search', 'Asset#get_assets')
Router.post('/api/assets', 'Asset#cadastrar_ativo')


