from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import User, Service, ServiceCategory

admin_bp = Blueprint('admin', __name__, template_folder='templates')


def admin_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    services = Service.query.all()
    return render_template('admin/dashboard.html', users=users, services=services)


@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form.get('description')
        cat = ServiceCategory(name=name, description=desc)
        db.session.add(cat)
        db.session.commit()
        flash('Category created')
        return redirect(url_for('admin.categories'))
    cats = ServiceCategory.query.all()
    return render_template('admin/categories.html', categories=cats)
