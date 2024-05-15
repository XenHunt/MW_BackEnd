from passlib.hash import pbkdf2_sha256 as sha256

from main import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column("firstname", db.String(120), nullable=True)
    lastName = db.Column("lastname", db.String(120), nullable=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(120), nullable=True)

    def __init__(
        self, firstName: str, lastName: str, username: str, password: str, role: str
    ):
        self.firstName = firstName
        self.lastName = lastName
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
                "firstName": x.firstName,
                "lastName": x.lastName,
                "role": x.role,
                "id": x.id,
            }

        return {"users": list(map(lambda x: to_json(x), UserModel.query.all()))}

    @staticmethod
    def generate_hash(password: str):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password: str, hash: str):
        return sha256.verify(password, hash)

    @staticmethod
    def findById(id: int):
        return UserModel.query.filter_by(id=id).first()

    def updateToDb(self):
        db.session.commit()


class RevokedTokenModel(db.Model):
    __tablename__ = "bad_tokens"
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jwt = db.Column(db.String(120), nullable=False, index=True, primary_key=True)
    expires_date = db.Column(db.DateTime, nullable=False, index=True)
    uid = db.Column(db.String(120), nullable=False)
    system_string = db.Column(db.String(120), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, jwt, expires_date, uid, system_string):
        self.uid = uid
        self.system_string = system_string
        self.jwt = jwt
        self.expires_date = expires_date

    def add(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def find_and_revoke(jwt: str, uid: str, system_string: str):
        qr = (
            db.session.query(RevokedTokenModel)
            .filter_by(jwt=jwt, uid=uid, system_string=system_string)
            .first()
        )
        if qr is None:
            return
        qr.revoke()

    def revoke(self):
        self.revoked = True
        db.session.commit()

    @classmethod
    def is_jwt_in_blacklisted(cls, jwt: str, uid: str, system_string: str):
        qr = (
            db.session.query(RevokedTokenModel)
            .filter_by(jwt=jwt, uid=uid, system_string=system_string)
            .first()
        )
        return True if qr is None else qr.revoked

    # @staticmethod
    # def create(jwt: str, expires_date: datetime):
    #     return RevokedTokenModel(jwt=jwt, expires_date=expires_date)


class Customer(db.Model):
    __tablename__ = "customers"

    customer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    firstname = db.Column(db.String(45), nullable=False)
    lastname = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(45), nullable=False)
    phone = db.Column(db.String(45), nullable=False)
    activebool = db.Column(db.Boolean, nullable=False, default=True)
    # create_date = db.Column(db.Date, nullable=False)
    # created_by = db.Column(db.String(45), nullable=False)
    # last_update = db.Column(db.Date, nullable=False)
    # last_update_by = db.Column(db.String(45), nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def findById(cls, id: int):
        return cls.query.filter_by(id=id).first()


class MeetModel(db.Model):
    __tablename__ = "meetings"
    meet_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    address = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(45), nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def findById(cls, id: int):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {"id": x.meet_id, "address": x.address, "description": x.description}

        return {"meetings": list(map(lambda x: to_json(x), MeetModel.query.all()))}


class CustomersMeets(db.Model):
    __tablename__ = "customers_meets"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    customers_id = db.Column(
        db.SmallInteger, db.ForeignKey("customers.customer_id"), nullable=False
    )
    meet_id = db.Column(db.Integer, db.ForeignKey("meetings.meet_id"), nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def findById(cls, id: int):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {"id": x.id, "customer_id": x.id, "meet_id": x.meet_id}

        return {
            "meetings_customers": list(
                map(lambda x: to_json(x), CustomersMeets.query.all())
            )
        }


class ClientEvent(db.Model):
    __tablename__ = "client_event"
    id_client = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    id_event = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    id = db.Column(db.Integer, autoincrement=True)


class Cashflow(db.Model):
    __tablename__ = "cashflow"
    type = db.Column(db.Integer)
    value = db.Column(db.Integer)
    detail = db.Column(db.String(120))

    id_event = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    id_payer = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    id = db.Column(db.Integer, autoincrement=True)


class Event(db.Model):
    __tablename__ = "event"
    id = db.Column(
        db.Integer,
        db.ForeignKey("client_event.id_event"),
        db.ForeignKey("cashflow.id_event"),
        primary_key=True,
    )
    title = db.Column(db.String(120))
    ev_time = db.Column(db.Time)
    ev_date = db.Column(db.Date)
    adress = db.Column(db.String(120))
    price = db.Column(db.Integer)


class Client(db.Model):
    __tablename__ = "client"
    pay_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey("client_event.id_client"))
    fio = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(60))
    passport = db.Column(db.String(12))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    b_date = db.Column(db.Date)
    children = db.Column(db.Boolean)
    photo = db.Column(db.String(40))


class Counterparty(db.Model):
    __tablename__ = "counterparty"
    id = db.Column(db.Integer, autoincrement=True)
    title = db.Column(db.String(120))
    pay_id = db.Column(db.Integer, primary_key=True)


class Payer(db.Model):
    __tablename__ = "payer"
    id = db.Column(
        db.Integer,
        db.ForeignKey("counterparty.pay_id"),
        db.ForeignKey("cashflow.id_payer"),
        db.ForeignKey("client.pay_id"),
    )
    payer_type = db.Column(db.Integer, primary_key=True)


class Det_P(db.Model):
    __tablename__ = "det_p"
    id = db.Column(db.Integer, db.ForeignKey("payer.payer_type"), primary_key=True)
    title = db.Column(db.String(40))
