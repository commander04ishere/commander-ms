from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

from app.routes.main import main_bp


# =====================================
# EXTENSIONS
# =====================================

db = SQLAlchemy()

migrate = Migrate()

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading"
)


# =====================================
# CREATE APP
# =====================================

def create_app():

    print("Creating app...")

    app = Flask(__name__)

    app.config.from_object(
        "config.Config"
    )

    # =================================
    # DATABASE
    # =================================

    db.init_app(app)

    migrate.init_app(
        app,
        db
    )

    # =================================
    # SOCKET.IO
    # =================================

    socketio.init_app(
        app
    )

    # =================================
    # MODELS
    # =================================

    from app.models.user import User
    from app.models.chat import Chat
    from app.models.chat_member import ChatMember
    from app.models.message import Message

    # =================================
    # CREATE DATABASE TABLES
    # =================================

    with app.app_context():

        print("Creating database tables...")

        db.create_all()

        print("Database tables created!")

    # =================================
    # ROUTES
    # =================================

    from app.routes.auth import auth_bp
    from app.routes.messenger import messenger_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        messenger_bp
    )

    app.register_blueprint(
        profile_bp
    )

    app.register_blueprint(
        main_bp
    )

    # =================================
    # SOCKET EVENTS
    # =================================

    from app.sockets import chat

    print("App created!")

    return app
