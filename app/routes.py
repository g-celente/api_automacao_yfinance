from mvc_flask import Router


# Define routes for the application
Router.post('/api/login', 'User#login')
Router.post('/api/register', 'User#register')