from mvc_flask import Router
from flask import jsonify


# Health check route
Router.get('/api/health', 'Health#get_health')

# Rotas para Usuários Administrativos
Router.post('/api/login', 'User#login')
Router.post('/api/register', 'User#register')
Router.post('/api/logout', 'User#logout')

# Rotas para Ativos
Router.post('/api/assets/search', 'Asset#get_assets')

