from datetime import timedelta

from flask import Flask
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
pg_user = "postgres"
pg_pass = "postgres123"
pg_port = "5432"
pg_db = "ModernWebDB"
pg_host = "localhost"
secret_key = "Dark Prince Of Pleasure"

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# app.config['PROPAGATE_EXCEPTIONS'] = True
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["SECRET_KEY"] = secret_key
app.config["SCHEDULER_API_ENABLED"] = True

db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app, supports_credentials=True)
scheduler = APScheduler()
scheduler.init_app(app)

import decorators  # noqa: E402, F401
import events  # noqa: F401, E402

# import orm  # noqa: E402, F401
import services  # noqa: E402, F401, E401

# @app.before_request
# def create_tables():
#     db.create_all()


with app.app_context():
    db.create_all()

scheduler.start()

# api.add_resource(services.Allusers, "/users")
# api.add_resource(services.UserRegistration, "/regs")
# api.add_resource(services.UserLogin, "/login")
# db.create_all()
