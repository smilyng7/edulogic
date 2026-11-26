"""Factory Flask para EduLogic."""
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from sqlalchemy.exc import IntegrityError
from .config import Config
from .extensions import db, cors
from . import models  # registra todas las tablas

def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, static_folder="../../frontend", static_url_path="/static")
    app.config.from_object(Config)
    if test_config: app.config.update(test_config)
    Path(app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True) if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:///") else None
    db.init_app(app); cors.init_app(app, origins=app.config.get("CORS_ORIGINS", "*"))
    from .routes import api
    app.register_blueprint(api)
    @app.get("/")
    def index(): 
        return send_from_directory(app.static_folder, "index.html")
    
    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        db.session.rollback()
        return jsonify(error={"code":"conflict", "message":"El registro duplica información o está relacionado con otros datos."}), 409
    
    @app.errorhandler(404)
    def not_found(error): 
        return jsonify(error={"code":"not_found", "message":"Recurso no encontrado."}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify(error={"code":"internal_error", "message":"Ocurrió un error procesando la solicitud."}), 500
    return app
