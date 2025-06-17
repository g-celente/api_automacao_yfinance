from mvc_flask import Router
from flask import jsonify


# Health check route
Router.get('/api/health', 'Health#get_health')

# Define routes for the application
Router.post('/api/login', 'User#login')
Router.post('/api/register', 'User#register')
Router.post('/api/logout', 'User#logout')