from flask import request, jsonify
from app.services.User_service import UserService

class UserController:

    def register(self):
        data = request.get_json()
        response, status = UserService.register(data)
        return jsonify(response), status

    def login(self):
        data = request.get_json()
        response, status = UserService.login(data)
        return jsonify(response), status
