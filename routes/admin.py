from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import User, db
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Admin':
            flash('Accès non autorisé. Vous devez être administrateur.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/pending-users')
@login_required
@admin_required
def pending_users():
    users = User.query.filter_by(role='Pending').all()
    return render_template('admin/pending_users.html', users=users)

@admin.route('/user/<int:user_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'Pending':
        user.role = 'User'
        user.is_active = True
        db.session.commit()
        flash(f'L\'utilisateur {user.username} a été approuvé avec succès.', 'success')
    return jsonify({'success': True})

@admin.route('/user/<int:user_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'Pending':
        db.session.delete(user)
        db.session.commit()
        flash(f'L\'utilisateur {user.username} a été rejeté.', 'success')
    return jsonify({'success': True})
