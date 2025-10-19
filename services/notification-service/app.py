from flask import Flask, jsonify, request
from flask_mail import Mail, Message
import os
import requests

app = Flask(__name__)

# Email Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')

mail = Mail(app)

@app.route('/notifications/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'notification'})

@app.route('/notifications', methods=['POST'])
def send_notification():
    data = request.json
    
    if data['type'] == 'booking_created':
        # Get user details from auth service
        auth_url = f"{os.getenv('AUTH_SERVICE_URL')}/users/{data['user_id']}"
        user_response = requests.get(auth_url)
        if user_response.status_code != 200:
            return jsonify({'error': 'User not found'}), 404
        
        user = user_response.json()
        
        # Get booking details from booking service
        booking_url = f"{os.getenv('BOOKING_SERVICE_URL')}/bookings/{data['booking_id']}"
        booking_response = requests.get(booking_url)
        if booking_response.status_code != 200:
            return jsonify({'error': 'Booking not found'}), 404
        
        booking = booking_response.json()
        
        # Send email
        msg = Message(
            'Booking Confirmation',
            recipients=[user['email']]
        )
        msg.body = f"""
        Dear {user['name']},
        
        Your booking has been confirmed.
        Date: {booking['start_time']}
        Duration: {booking['end_time']}
        
        Thank you for using our service!
        """
        
        mail.send(msg)
        
        return jsonify({'status': 'notification sent'})
    
    return jsonify({'error': 'Invalid notification type'}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5004))
    app.run(host='0.0.0.0', port=port)