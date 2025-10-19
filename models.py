from extensions import db
from flask_login import UserMixin
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as sha256


class Role:
    ADMIN = 'admin'
    STAFF = 'staff'
    CUSTOMER = 'customer'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(120))
    role = db.Column(db.String(20), default=Role.CUSTOMER)
    phone = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Customer bookings (where user is the customer)
    bookings = db.relationship(
        'Booking',
        back_populates='customer',
        lazy=True,
        foreign_keys='Booking.user_id'
    )
    
    # Staff bookings (where user is the assigned staff)
    assigned_bookings = db.relationship(
        'Booking',
        back_populates='staff',
        lazy=True,
        foreign_keys='Booking.staff_id',
        overlaps="staff,bookings"
    )

    def set_password(self, password):
        self.password_hash = sha256.hash(password)

    def check_password(self, password):
        return sha256.verify(password, self.password_hash)


class ServiceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    services = db.relationship('Service', backref='category', lazy=True)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('service_category.id'))

    bookings = db.relationship('Booking', backref='service', lazy=True)


class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    bio = db.Column(db.Text)
    skills = db.Column(db.String(250))

    user = db.relationship('User', backref=db.backref('staff_profile', uselist=False))


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default='booked')  # booked, cancelled, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to the staff User (if any). Backref 'staff_member' is defined on User.assigned_bookings
    # Relationship to customer who booked
    customer = db.relationship(
        'User',
        back_populates='bookings',
        foreign_keys=[user_id]
    )
    
    # Relationship to assigned staff member
    staff = db.relationship(
        'User',
        back_populates='assigned_bookings',
        foreign_keys=[staff_id],
        overlaps="customer,bookings"
    )
