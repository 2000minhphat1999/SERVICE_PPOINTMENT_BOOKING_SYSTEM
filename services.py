from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Service, ServiceCategory

services_bp = Blueprint('services', __name__, template_folder='templates')


@services_bp.route('/')
def list_services():
    services = Service.query.all()
    categories = ServiceCategory.query.all()
    return render_template('services/list.html', services=services, categories=categories)


@services_bp.route('/<int:service_id>')
def view_service(service_id):
    service = Service.query.get_or_404(service_id)
    return render_template('services/view.html', service=service)


@services_bp.route('/create', methods=['GET', 'POST'])
def create_service():
    # Simplified: no auth check here (should be admin only)
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        duration = int(request.form['duration'])
        desc = request.form.get('description')
        category_id = request.form.get('category_id')
        svc = Service(name=name, price=price, duration_minutes=duration, description=desc, category_id=category_id)
        db.session.add(svc)
        db.session.commit()
        flash('Service created')
        return redirect(url_for('services.list_services'))
    categories = ServiceCategory.query.all()
    return render_template('services/create.html', categories=categories)


@services_bp.route('/<int:service_id>/delete', methods=['POST'])
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    # TODO: Add proper authorization check
    # TODO: Check if service has any bookings before deleting
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully')
    return redirect(url_for('services.list_services'))
