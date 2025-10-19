from flask import Flask
from dotenv import load_dotenv
from extensions import db, login_manager, mail, scheduler
import os

load_dotenv()


def create_app(config_object=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///data.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail (console)
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 25))
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Add initial data if database is empty
        if not os.path.exists('instance/data.sqlite'):
            from models import User, Role, ServiceCategory
            # Create admin user
            admin = User.query.filter_by(email='admin@example.com').first()
            if not admin:
                admin = User(
                    email='admin@example.com',
                    name='Admin User',
                    role=Role.ADMIN
                )
                admin.set_password('admin123')  # Change this in production!
                db.session.add(admin)
            
            # Create default service categories
            categories = ['Haircut', 'Massage', 'Nail Care', 'Facial']
            for cat_name in categories:
                if not ServiceCategory.query.filter_by(name=cat_name).first():
                    cat = ServiceCategory(name=cat_name)
                    db.session.add(cat)
            
            db.session.commit()

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from auth import auth_bp
    from services import services_bp
    from bookings import bookings_bp
    from admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(services_bp, url_prefix='/services')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Scheduler
    scheduler.start()

    return app


if __name__ == '__main__':
    # Allows running with: python app.py
    # Uses PORT and HOST environment variables when present (PowerShell example below)
    app = create_app()
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    # Set FLASK_DEBUG=1 to enable debug mode when running directly
    debug = os.getenv('FLASK_DEBUG', '1') in ('1', 'true', 'True')
    print(f"Starting app on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
