from mvc_flask import Router
from flask import jsonify


# Health check route
@Router.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


# Define routes for the application
Router.post('/api/login', 'User#login')
Router.post('/api/register', 'User#register')