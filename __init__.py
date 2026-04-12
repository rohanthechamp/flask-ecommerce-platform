from flask import Flask
from flask_bootstrap import Bootstrap5
import secrets
import os
from extensions import db, login_manager, cache, oauth, migrate
from auth import auth_bp
from admin import admin_bp
from main import main_bp

# Function to create the database tables
def create_database(app):
    with app.app_context():
        db.create_all()
        print("Database Synced")

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config["SECRET_KEY"] = secrets.token_urlsafe(16)
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    
    # Cache Config
    app.config["CACHE_TYPE"] = "RedisCache"
    app.config["CACHE_REDIS_HOST"] = os.getenv("CACHE_REDIS_HOST")
    app.config["CACHE_REDIS_PORT"] = int(os.getenv("CACHE_REDIS_PORT"))
    app.config["CACHE_REDIS_DB"] = int(os.getenv("CACHE_REDIS_DB"))

    # Initialize extensions
    Bootstrap5(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)
    oauth.init_app(app)
    
    # Authlib Google OAuth setup
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    oauth.register(
        name="google",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    # Register blueprints
    app.register_blueprint(main_bp)      # e.g. /get_all_items -> url_for('main.get_all_items')
    app.register_blueprint(auth_bp)      # e.g. /login -> url_for('auth.login')
    app.register_blueprint(admin_bp)     # e.g. /admin_panel -> url_for('admin.admin_panel')

    # Ensure Database structures exist
    create_database(app)

    return app
