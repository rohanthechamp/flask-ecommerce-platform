from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate
import redis
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()

# Setup LoginManager defaults
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

cache = Cache()
oauth = OAuth()
migrate = Migrate()

CACHE_REDIS_HOST = os.getenv("CACHE_REDIS_HOST", "localhost")
CACHE_REDIS_PORT = int(os.getenv("CACHE_REDIS_PORT", 6379))
CACHE_REDIS_DB = int(os.getenv("CACHE_REDIS_DB", 0))

redis_client = redis.Redis(
    host=CACHE_REDIS_HOST,
    port=CACHE_REDIS_PORT,
    db=CACHE_REDIS_DB,
    decode_responses=True,
)
