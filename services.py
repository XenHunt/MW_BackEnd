from flask_restful import Resource, reqparse
from flask import jsonify
from main import db
from orm import UserModel

from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

parser = reqparse.RequestParser()
parser.add_argument('username', required = True)
parser.add_argument('password', required = True)
parser.add_argument('firstname', required = False)
parser.add_argument('lastname', required = False)
parser.add_argument('role', required = True)


class Allusers(Resource):
    def get(self):
        return UserModel.return_all()
    
class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        
        if UserModel.find_by_username(data['username']):
            return {'message': f'User {data["username"]} already exists'}, 400
        
        new_user = UserModel(
            username = data['username'],
            password = UserModel.generate_hash(data['password']),
            role = data['role'],
            firstname = data['firstname'],
            lastname = data['lastname']
        )
        
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {'message': 'User created successfully',
                    'access_token': access_token,
                    'refresh_token': refresh_token
                    }, 201
        except Exception as e:
            return {'message': str(e)}, 500
        