from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db, mail, scheduler
from models import Booking, Service, User
from datetime import datetime, timedelta
from flask_mail import Message

bookings_bp = Blueprint('bookings', __name__, template_folder='templates')


@bookings_bp.route('/')
@login_required
def list_bookings():
    if current_user.role == 'admin':
        # Admins see all bookings
        bookings = Booking.query.order_by(Booking.start_time.desc()).all()
    elif current_user.role == 'staff':
        # Staff sees bookings assigned to them
        bookings = Booking.query.filter_by(staff_id=current_user.id).order_by(Booking.start_time.desc()).all()
    else:
        # Customers see their own bookings
        bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_time.desc()).all()
    
    return render_template('bookings/list.html', bookings=bookings)

@bookings_bp.route('/calendar')
@login_required
def calendar():
    # very simple list
    upcoming = Booking.query.filter(Booking.start_time >= datetime.utcnow()).order_by(Booking.start_time).all()
    return render_template('bookings/calendar.html', bookings=upcoming)


@bookings_bp.route('/create/<int:service_id>', methods=['GET', 'POST'])
@login_required
def create_booking(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == 'POST':
        start_str = request.form['start_time']
        staff_id = request.form.get('staff_id')
        start_time = datetime.fromisoformat(start_str)
        end_time = start_time + timedelta(minutes=service.duration_minutes)
        booking = Booking(user_id=current_user.id, service_id=service.id, staff_id=staff_id, start_time=start_time, end_time=end_time)
        db.session.add(booking)
        db.session.commit()

        # send confirmation (console)
        send_booking_email(current_user.email, booking)

        # schedule reminder 1 day before
        run_date = booking.start_time - timedelta(days=1)
        job_id = f"remind_{booking.id}"
        try:
            scheduler.add_job(func=send_reminder, trigger='date', run_date=run_date, args=[booking.id], id=job_id)
        except Exception:
            pass

        flash('Booking created')
        return redirect(url_for('bookings.calendar'))
    staff = User.query.filter_by(role='staff').all()
    return render_template('bookings/create.html', service=service, staff=staff)


@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and current_user.role != 'admin':
        flash('Not allowed')
        return redirect(url_for('bookings.calendar'))
    booking.status = 'cancelled'
    db.session.commit()
    flash('Cancelled')
    return redirect(url_for('bookings.calendar'))


def send_booking_email(email, booking):
    try:
        msg = Message(subject='Booking confirmation', recipients=[email], body=f'Your booking #{booking.id} is confirmed for {booking.start_time}')
        mail.send(msg)
    except Exception as e:
        print('Mail send error', e)


def send_reminder(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return
    try:
        msg = Message(subject='Booking reminder', recipients=[booking.user.email], body=f'Reminder for booking #{booking.id} at {booking.start_time}')
        mail.send(msg)
    except Exception as e:
        print('Reminder send error', e)
