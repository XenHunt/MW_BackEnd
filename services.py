from datetime import datetime
from parser import parserId, parserLogin, parserRegister, parserUpdate

from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt_identity,
    jwt_required,
)
from flask_jwt_extended.utils import get_jwt
from sqlalchemy.sql.functions import count

from main import app, db
from orm import Customer, CustomersMeets, MeetModel, RevokedTokenModel, UserModel


@app.route("/customers-meetings", methods=["POST"])
def customers_meetings():
    def to_json(x):
        return {
            "customer_id": x.CustomersMeets.customers_id,
            "firstName": x.Customer.firstname,
            "lastName": x.Customer.lastname,
            "id": x.CustomersMeets.id,
            "meet_id": x.CustomersMeets.meet_id,
            "address": x.MeetModel.address,
            "description": x.MeetModel.description,
        }

    query = (
        db.session.query(CustomersMeets, Customer, MeetModel)
        .filter(
            CustomersMeets.customers_id == Customer.customer_id,
        )
        .filter(CustomersMeets.meet_id == MeetModel.meet_id)
    )

    return {"meetings_customers": list(map(lambda x: to_json(x), query.all()))}


@app.route("/group_by-adress", methods=["GET"])
def group_by_adress():
    querry = (
        db.session.query(
            count(CustomersMeets.id),
            MeetModel.address,
        )
        .filter(CustomersMeets.meet_id == MeetModel.meet_id)
        .group_by(MeetModel.meet_id)
    )

    # grouped_querry = query.group_by(MeetModel.address).all()
    def to_json(x):
        return {
            "count": x[0],
            "address": x[1],
        }

    return {"ga": list(map(lambda x: to_json(x), querry.all()))}


@app.route("/users", methods=["POST"])
@jwt_required()
def users():
    return UserModel.return_all()


@app.route("/update-user", methods=["POST"])
@jwt_required()
def updateUser():
    data = parserUpdate.parse_args()
    user = UserModel.findById(data["id"])
    if user:
        user.username = data["username"] if data["username"] else user.username
        user.password = (
            UserModel.generate_hash(data["password"])
            if data["password"]
            else user.password
        )
        user.firstName = data["firstName"] if data["firstName"] else user.firsNname
        user.lastName = data["lastName"] if data["lastName"] else user.lastName
        user.role = data["role"] if data["role"] else user.role
        user.updateToDb()
    else:
        return jsonify({"message": "User not found"}), 404
    return {"message": "User updated"}


@app.route("/register", methods=["POST"])
def register():
    data = parserRegister.parse_args()
    id = parserId.parse_args()
    if UserModel.find_by_username(data["username"]):
        return jsonify({"message": f'User {data["username"]} already exists'}), 400
    new_user = UserModel(
        username=data["username"],
        password=UserModel.generate_hash(data["password"]),
        role=data["role"],
        firstName=data["firstName"],
        lastName=data["lastName"],
    )
    try:
        new_user.save_to_db()
        access_token = create_access_token(identity=data["username"])
        dec_acc = decode_token(access_token)
        refresh_token = create_refresh_token(identity=data["username"])
        dec_ref = decode_token(refresh_token)
        RevokedTokenModel(
            dec_acc["jti"],
            datetime.fromtimestamp(dec_acc["exp"]),
            id["uid"],
            id["system_string"],
        ).add()
        RevokedTokenModel(
            dec_ref["jti"],
            datetime.fromtimestamp(dec_ref["exp"]),
            id["uid"],
            id["system_string"],
        ).add()
        return {
            # "message": "User created successfully",
            "id": new_user.id,
            "username": new_user.username,
            "firstName": new_user.firstName,
            "lastName": new_user.lastName,
            "role": new_user.role,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 201
    except Exception as e:
        return {"message": str(e)}, 500


@app.route("/login", methods=["POST"])
def login():
    data = parserLogin.parse_args()
    id = parserId.parse_args()
    user = UserModel.find_by_username(data["username"])
    if user and UserModel.verify_hash(data["password"], user.password):
        access_token = create_access_token(identity=data["username"])
        dec_acc = decode_token(access_token)
        refresh_token = create_refresh_token(identity=data["username"])
        dec_ref = decode_token(refresh_token)
        RevokedTokenModel(
            dec_acc["jti"],
            datetime.fromtimestamp(dec_acc["exp"]),
            id["uid"],
            id["system_string"],
        ).add()
        RevokedTokenModel(
            dec_ref["jti"],
            datetime.fromtimestamp(dec_ref["exp"]),
            id["uid"],
            id["system_string"],
        ).add()
        return {
            "id": user.id,
            "username": user.username,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "role": user.role,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 200
    else:
        return {"message": "Wrong credentials"}, 401


# TODO: Теперь надо сделать очищение токенов при запросах с Angular
@app.route("/logout", methods=["POST"])
@jwt_required(refresh=True)
def logout():
    refresh_token = get_jwt()["jti"]
    id = parserId.parse_args()
    RevokedTokenModel.find_and_revoke(refresh_token, id["uid"], id["system_string"])
    RevokedTokenModel.find_and_revoke(
        decode_token(id["access_token"], allow_expired=True)["jti"],
        id["uid"],
        id["system_string"],
    )
    return {"message": "Successfully logged out"}, 200


@app.route("/protected-refresh", methods=["GET", "POST"])
@jwt_required(refresh=True)
# @not_blacklisted_token
def protected():
    return {"message": "protected_refresh"}, 200


@app.route("/protected-access", methods=["GET", "POST"])
@jwt_required()
# @not_blacklisted_token
def protected_access():
    return {"message": "protected_access"}, 200


@app.route("/refresh-access", methods=["POST"])
@jwt_required(
    refresh=True,
)
def refresh_access():
    id = parserId.parse_args()
    RevokedTokenModel.find_and_revoke(
        decode_token(id["access_token"], allow_expired=True)["jti"],
        id["uid"],
        id["system_string"],
    )
    username = get_jwt_identity()
    access_token = create_access_token(identity=username)
    dec_acc = decode_token(access_token)
    RevokedTokenModel(
        dec_acc["jti"],
        datetime.fromtimestamp(dec_acc["exp"]),
        id["uid"],
        id["system_string"],
    ).add()
    return {"access_token": access_token}, 200


@app.route("/refresh-refresh", methods=["POST"])
@jwt_required(
    refresh=True,
)
def refresh_refresh():
    username = get_jwt_identity()
    id = parserId.parse_args()
    RevokedTokenModel.find_and_revoke(get_jwt()["jti"], id["uid"], id["system_string"])
    RevokedTokenModel.find_and_revoke(
        decode_token(id["access_token"], allow_expired=True)["jti"],
        id["uid"],
        id["system_string"],
    )
    refresh_token = create_refresh_token(identity=username)
    dec_ref = decode_token(refresh_token)
    RevokedTokenModel(
        dec_ref["jti"],
        datetime.fromtimestamp(dec_ref["exp"]),
        id["uid"],
        id["system_string"],
    ).add()
    access_token = create_access_token(identity=username)
    dec_acc = decode_token(access_token)
    RevokedTokenModel(
        dec_acc["jti"],
        datetime.fromtimestamp(dec_acc["exp"]),
        id["uid"],
        id["system_string"],
    ).add()
    return {"refresh_token": refresh_token, "access_token": access_token}, 200
