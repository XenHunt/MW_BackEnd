from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
cors = CORS(app, supports_credentials=True)
pg_user = "postgres"
pg_pass = "postgres123"
pg_port = "5432"
pg_db = "ModernWebDB"
pg_host = "localhost"

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config['PROPAGATE_EXCEPTIONS'] = True
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
app.config["SECRET_KEY"] = "some-secret-string"

db = SQLAlchemy(app)
jwt = JWTManager(app)

# import orm  # noqa: E402, F401
# import services  # noqa: E402


@app.before_request
def create_tables():
    db.create_all()


# api.add_resource(services.Allusers, "/users")
# api.add_resource(services.UserRegistration, "/regs")
# api.add_resource(services.UserLogin, "/login")
# db.create_all()
