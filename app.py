import os
import logging
from flask_wtf.csrf import CSRFProtect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")  # Changed from SESSION_SECRET to SECRET_KEY
csrf = CSRFProtect(app)  

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///ccms.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize CSRF protection
csrf = CSRFProtect(app)  # Added for form security

# Initialize the app with the extension
db.init_app(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Add this after creating your Flask app but before your routes
@app.context_processor
def inject_now():
    return {'now': datetime.now}

# Import models here (outside app context) to avoid circular imports
from models import User, Event, Club, Registration

# Import routes after models
import routes

# Create tables within application context
with app.app_context():
    db.create_all()