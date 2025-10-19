"""
Database initialization script.
Run this script directly to create tables and add initial data:
python init_db.py
"""
from app import create_app, db
from models import User, Role, ServiceCategory, Service

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                name='Admin User',
                role=Role.ADMIN
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            print("Created admin user (admin@example.com)")
        
        # Create default service categories
        categories = [
            ('Haircut', 'Various haircut services'),
            ('Massage', 'Relaxing massage treatments'),
            ('Nail Care', 'Manicure and pedicure services'),
            ('Facial', 'Facial treatments and skincare')
        ]
        
        for name, desc in categories:
            if not ServiceCategory.query.filter_by(name=name).first():
                cat = ServiceCategory(name=name, description=desc)
                db.session.add(cat)
                print(f"Created category: {name}")
        
        # Add some sample services
        haircut_cat = ServiceCategory.query.filter_by(name='Haircut').first()
        if haircut_cat and not Service.query.first():
            services = [
                ('Men\'s Haircut', 'Basic men\'s haircut service', 30.0, 30),
                ('Women\'s Haircut', 'Haircut and basic styling', 50.0, 45),
                ('Kids Haircut', 'Haircut for children under 12', 25.0, 30),
            ]
            
            for name, desc, price, duration in services:
                svc = Service(
                    name=name,
                    description=desc,
                    price=price,
                    duration_minutes=duration,
                    category_id=haircut_cat.id
                )
                db.session.add(svc)
                print(f"Created service: {name}")
        
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()