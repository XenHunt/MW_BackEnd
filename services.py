from datetime import timedelta

from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import reqparse

from main import app
from orm import UserModel

parser = reqparse.RequestParser()
parser.add_argument("username", required=True)
parser.add_argument("password", required=True)
parser.add_argument("firstname", required=False)
parser.add_argument("lastname", required=False)
parser.add_argument("role", required=False)


@app.route("/users", methods=["GET"])
def users():
    return UserModel.return_all()


@app.route("/register", methods=["POST"])
def register():
    data = parser.parse_args()
    if UserModel.find_by_username(data["username"]):
        return jsonify({"message": f'User {data["username"]} already exists'}), 400
    new_user = UserModel(
        username=data["username"],
        password=UserModel.generate_hash(data["password"]),
        role=data["role"],
        firstname=data["firstname"],
        lastname=data["lastname"],
    )
    try:
        new_user.save_to_db()
        access_token = create_access_token(
            identity=data["username"], expires_delta=timedelta(seconds=30)
        )
        refresh_token = create_refresh_token(identity=data["username"])
        return {
            # "message": "User created successfully",
            "id": new_user.id,
            "username": new_user.username,
            "firstname": new_user.firstname,
            "lastname": new_user.lastname,
            "role": new_user.role,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 201
    except Exception as e:
        return {"message": str(e)}, 500


@app.route("/login", methods=["POST"])
def login():
    data = parser.parse_args()
    user = UserModel.find_by_username(data["username"])
    if user and UserModel.verify_hash(data["password"], user.password):
        access_token = create_access_token(
            identity=data["username"], expires_delta=timedelta(seconds=30)
        )
        refresh_token = create_refresh_token(identity=data["username"])
        return {
            "id": user.id,
            "username": user.username,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "role": user.role,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 200
    else:
        return {"message": "Wrong credentials"}, 401


# TODO: Теперь надо сделать очищение токенов при запросах с Angular
@app.route("/logout", methods=["POST"])
def logout():
    return {"message": "Successfully logged out"}, 200


# class Allusers(Resource):
#     # @jwt_required()
#     def get(self):
#         return UserModel.return_all()
#
#
# class UserRegistration(Resource):
#     def post(self):
#         data = parser.parse_args()
#
#         if UserModel.find_by_username(data["username"]):
#             return {"message": f'User {data["username"]} already exists'}, 400
#
#         new_user = UserModel(
#             username=data["username"],
#             password=UserModel.generate_hash(data["password"]),
#             role=data["role"],
#             firstname=data["firstname"],
#             lastname=data["lastname"],
#         )
#
#         try:
#             new_user.save_to_db()
#             access_token = create_access_token(
#                 identity=data["username"], expires_delta=timedelta(seconds=30)
#             )
#             refresh_token = create_refresh_token(identity=data["username"])
#             return {
#                 # "message": "User created successfully",
#                 "id": new_user.id,
#                 "username": new_user.username,
#                 "firstname": new_user.firstname,
#                 "lastname": new_user.lastname,
#                 "role": new_user.role,
#                 "access_token": access_token,
#                 "refresh_token": refresh_token,
#             }, 201
#         except Exception as e:
#             return {"message": str(e)}, 500
#
#
# class UserLogin(Resource):
#     def post(self):
#         data = parser.parse_args()
#         current_user = UserModel.find_by_username(data["username"])
#         print(current_user)
#         if not current_user:
#             return {"message": f"User {data['username']} doesn't exists"}, 401
#
#         if UserModel.verify_hash(data["password"], current_user.password):
#             access_token = create_access_token(
#                 identity=data["username"], expires_delta=timedelta(seconds=30)
#             )
#             refresh_token = create_refresh_token(identity=data["username"])
#             return {
#                 "id": current_user.id,
#                 "username": current_user.username,
#                 "firstname": current_user.firstname,
#                 "lastname": current_user.lastname,
#                 "role": current_user.role,
#                 "access_token": access_token,
#                 "refresh_token": refresh_token,
#             }, 200
#         return {"message": "Password is invalid"}, 401
#
#
# class UserLogoutAccess(Resource):
#     def post(self):
#         pass
#
#
# class UserLogoutRefresh(Resource):
#     def post(self):
#         pass
#
#
# class RefreshAccessToken(Resource):
#     def post(self):
#         pass
#
#
# class RefreshRefreshToken(Resource):
#     def post(self):
#         pass
