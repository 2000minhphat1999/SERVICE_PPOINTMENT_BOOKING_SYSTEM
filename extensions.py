from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize extensions without app context
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
scheduler = BackgroundScheduler()