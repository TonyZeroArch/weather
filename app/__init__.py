from flask import Flask

# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# from .config import Config
from .config import DevelopmentConfig, TestingConfig, ProductionConfig

# logging
from .utils.logger import configure_logger

# from .routes import main as main_blueprint

# db = SQLAlchemy()


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Console-only logging
    configure_logger(app, console_output=True, file_output=False)

    # db.init_app(app)
    CORS(app)

    # Register blueprint - import main directly from blueprint.py
    from app.routes.blueprint import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app
