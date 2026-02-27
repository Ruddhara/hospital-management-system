from flask import Flask
from flask_login import LoginManager
from .models import db, Admin, Doctor, Patient, Pharmacy
import os

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/medicore.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login_patient'

    @login_manager.user_loader
    def load_user(user_id):
        for model in [Admin, Doctor, Patient, Pharmacy]:
            user = model.query.get(int(user_id))
            if user:
                return user
        return None

    from .app import register_routes
    register_routes(app)

    return app

