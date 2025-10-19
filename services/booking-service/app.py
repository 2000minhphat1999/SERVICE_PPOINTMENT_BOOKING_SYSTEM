from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///bookings.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, nullable=False)
    staff_id = db.Column(db.Integer)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default='booked')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_id': self.service_id,
            'staff_id': self.staff_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

@app.route('/bookings/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'booking'})

@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.json
    
    # Validate service exists
    service_url = f"{os.getenv('SERVICE_CATALOG_URL')}/services/{data['service_id']}"
    service_response = requests.get(service_url)
    if service_response.status_code != 200:
        return jsonify({'error': 'Service not found'}), 404
    
    # Create booking
    booking = Booking(
        user_id=data['user_id'],
        service_id=data['service_id'],
        staff_id=data.get('staff_id'),
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        notes=data.get('notes')
    )
    
    db.session.add(booking)
    db.session.commit()
    
    # Notify notification service
    notification_url = f"{os.getenv('NOTIFICATION_SERVICE_URL')}/notifications"
    notification_data = {
        'type': 'booking_created',
        'booking_id': booking.id,
        'user_id': booking.user_id
    }
    requests.post(notification_url, json=notification_data)
    
    return jsonify(booking.to_dict()), 201

@app.route('/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return jsonify(booking.to_dict())

if __name__ == '__main__':
    db.create_all()
    port = int(os.getenv('PORT', 5003))
    app.run(host='0.0.0.0', port=port)