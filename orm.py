from passlib.hash import pbkdf2_sha256 as sha256

from main import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(120), nullable=True)
    lastname = db.Column(db.String(120), nullable=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(120), nullable=True)

    def __init__(
        self, firstname: str, lastname: str, username: str, password: str, role: str
    ):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password
        self.role = role

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                "username": x.username,
                "password": x.password,
            }

        return {"users": list(map(lambda x: to_json(x), UserModel.query.all()))}

    @staticmethod
    def generate_hash(password: str):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password: str, hash: str):
        return sha256.verify(password, hash)


class RevokedTokenModel(db.Model):
    __tablename__ = "bad_tokens"
    id = db.Column(db.Integer, primary_key=True)
    jwt = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jwt_in_blacklisted(cls, jwt):
        qr = db.session.query(jti=jwt).first()
        return bool(qr)
