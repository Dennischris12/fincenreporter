from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import stripe

# Initialize the app and related configurations
app = Flask(__name__)
app.config['EayVG20!9'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///boi_filing.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
stripe.api_key = 'your_stripe_api_key'

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Specify the login view

# Import routes after app and db initialization to avoid circular imports
from app import routes
