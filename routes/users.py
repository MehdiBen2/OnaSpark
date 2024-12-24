from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, Unit, Zone
from utils.decorators import admin_required
from utils.roles import UserRole

users = Blueprint('users', __name__)

@users.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.options(
        db.joinedload(User.assigned_zone),
        db.joinedload(User.assigned_unit)
    ).all()
    zones = Zone.query.order_by(Zone.name).all()
    zones_data = [{'id': zone.id, 'name': zone.name} for zone in zones]
    
    # Get available roles based on current user's role
    available_roles = [UserRole.UNIT, UserRole.ZONE, UserRole.EMPLOYER, UserRole.DIRECTEUR_ZONE, UserRole.DIRECTEUR_UNITE]
    if current_user.role in UserRole.ADMIN_ROLES:
        available_roles = [UserRole.ADMIN] + available_roles
    
    return render_template('admin/users.html', 
                         users=users, 
                         zones=zones, 
                         zones_data=zones_data,
                         UserRole=UserRole,
                         available_roles=available_roles,
                         current_user=current_user)  # Pass current_user and available_roles to template

@users.route('/admin/users/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    nickname = request.form.get('nickname')
    unit_id = request.form.get('unit_id')
    zone_id = request.form.get('zone_id')

    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.id != user_id:
        flash('Un utilisateur avec ce nom existe déjà.', 'error')
        return redirect(url_for('users.manage_users'))

    if role == 'Unit Officer':
        if not unit_id or not zone_id:
            flash('Un officier d\'unité doit avoir une zone et une unité assignées.', 'error')
            return redirect(url_for('users.manage_users'))
        
        unit = Unit.query.get(unit_id)
        if not unit or str(unit.zone_id) != zone_id:
            flash('L\'unité sélectionnée n\'appartient pas à la zone sélectionnée.', 'error')
            return redirect(url_for('users.manage_users'))
    else:
        unit_id = None

    user.username = username
    user.role = role
    if password:
        user.set_password(password)
    if nickname:
        user.nickname = nickname
    else:
        user.nickname = None
    user.unit_id = unit_id

    db.session.commit()
    flash('Utilisateur mis à jour avec succès.', 'success')
    return redirect(url_for('users.manage_users'))

@users.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@users.route('/admin/users/<int:user_id>/get')
@login_required
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'unit_id': user.unit_id,
        'zone_id': user.zone_id
    })

@users.route('/admin/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    nickname = request.form.get('nickname')
    unit_id = request.form.get('unit_id')
    zone_id = request.form.get('zone_id')

    if User.query.filter_by(username=username).first():
        flash('Un utilisateur avec ce nom existe déjà.', 'error')
        return redirect(url_for('users.manage_users'))

    if role not in UserRole.get_all_roles():
        flash('Rôle invalide.', 'error')
        return redirect(url_for('users.manage_users'))

    if UserRole.requires_unit(role) and (not unit_id or not zone_id):
        flash('Un employeur d\'unité doit avoir une zone et une unité assignées.', 'error')
        return redirect(url_for('users.manage_users'))

    if unit_id:
        unit = Unit.query.get(unit_id)
        if not unit or str(unit.zone_id) != zone_id:
            flash('L\'unité sélectionnée n\'appartient pas à la zone sélectionnée.', 'error')
            return redirect(url_for('users.manage_users'))

    user = User(
        username=username,
        role=role,
        nickname=nickname if nickname else None,
        unit_id=unit_id if UserRole.requires_unit(role) else None
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    flash('Utilisateur créé avec succès.', 'success')
    return redirect(url_for('users.manage_users'))

@users.route('/api/zones')
@login_required
def get_zones():
    zones = Zone.query.all()
    return jsonify([{'id': zone.id, 'name': zone.name} for zone in zones])

@users.route('/api/zones/<int:zone_id>/units')
@login_required
def get_zone_units(zone_id):
    try:
        zone = Zone.query.get_or_404(zone_id)
        units = Unit.query.filter_by(zone_id=zone_id).order_by(Unit.name).all()
        return jsonify({
            'success': True,
            'units': [{'id': unit.id, 'name': unit.name} for unit in units],
            'zone': {'id': zone.id, 'name': zone.name}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error fetching units: {str(e)}"
        }), 500

@users.route('/api/users', methods=['POST'])
@login_required
@admin_required
def api_create_user():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    nickname = data.get('nickname')
    zone_id = data.get('zone')
    unit_id = data.get('unit')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Un utilisateur avec ce nom existe déjà.'}), 400

    # Validate role-specific requirements
    if role in ['zone', 'unit'] and not zone_id:
        return jsonify({'message': 'Une zone doit être sélectionnée pour ce rôle.'}), 400
    
    if role == 'unit' and not unit_id:
        return jsonify({'message': 'Une unité doit être sélectionnée pour ce rôle.'}), 400

    # If unit is selected, verify it belongs to the selected zone
    if unit_id:
        unit = Unit.query.get(unit_id)
        if not unit or str(unit.zone_id) != str(zone_id):
            return jsonify({'message': 'L\'unité sélectionnée n\'appartient pas à la zone sélectionnée.'}), 400

    # Create new user
    new_user = User(
        username=username,
        nickname=nickname,
        role=role
    )
    new_user.set_password(password)
    
    if role in ['zone', 'unit']:
        new_user.zone_id = zone_id
    if role == 'unit':
        new_user.unit_id = unit_id

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Utilisateur créé avec succès'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erreur lors de la création de l\'utilisateur'}), 500
