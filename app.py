from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from utils.pdf_generator import create_incident_pdf
import random
from functools import wraps
from openpyxl import Workbook
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from models import db, User, Unit, Incident, Zone, Center
from routes.auth import auth
from routes.profiles import profiles
from routes.incidents import incidents
from routes.units import units
from routes.users import users
from routes.database_admin import database_admin
from routes.admin import admin
from flask.cli import with_appcontext
import click

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///OnaDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'warning'

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(profiles)
app.register_blueprint(incidents)
app.register_blueprint(units)
app.register_blueprint(users)
app.register_blueprint(database_admin)

@app.cli.command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the database."""
    from scripts.init_db import init_database
    init_database()
    click.echo('Initialized the database.')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['Admin', 'administrateur']:
            flash('Vous devez être administrateur pour accéder à cette page.', 'danger')
            return redirect(url_for('incidents.incident_list'))
        return f(*args, **kwargs)
    return decorated_function

def unit_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        # Skip unit requirement check for admin users
        if current_user.role in ['Admin', 'administrateur']:
            return f(*args, **kwargs)
        if not hasattr(current_user, 'unit_id') or current_user.unit_id is None:
            return redirect(url_for('select_unit'))
        return f(*args, **kwargs)
    return decorated_function

# Water and sanitation phrases
WATER_PHRASES = [
    "L'eau est l'essence de la vie ; préservons-la pour les générations futures.",
    "L'assainissement est une question de dignité ; assurons-le pour tous.",
    "Chaque goutte compte dans la préservation de nos ressources en eau.",
    "Un environnement propre commence par un bon assainissement.",
    "La qualité de l'eau reflète la santé de notre société.",
    "Protéger l'eau, c'est protéger la vie.",
    "L'assainissement est la clé d'un environnement sain.",
    "L'eau propre est un droit fondamental.",
    "Ensemble pour une meilleure gestion de l'eau.",
    "La propreté de l'eau est notre responsabilité collective."
]

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main_dashboard'))
    return render_template('landing.html')

@app.route('/main')
@login_required
def main_dashboard():
    # Get recent incidents (last 5)
    if current_user.role == 'Admin':
        recent_incidents = Incident.query.order_by(Incident.date_incident.desc()).limit(5).all()
    else:
        recent_incidents = Incident.query.filter_by(author=current_user).order_by(Incident.date_incident.desc()).limit(5).all()
    
    # Get statistics
    if current_user.role == 'Admin':
        total_incidents = Incident.query.count()
        resolved_incidents = Incident.query.filter_by(status='Résolu').count()
        pending_incidents = Incident.query.filter_by(status='En cours').count()
    else:
        total_incidents = Incident.query.filter_by(author=current_user).count()
        resolved_incidents = Incident.query.filter_by(author=current_user, status='Résolu').count()
        pending_incidents = Incident.query.filter_by(author=current_user, status='En cours').count()
    
    return render_template('main_dashboard.html',
                         recent_incidents=recent_incidents,
                         total_incidents=total_incidents,
                         resolved_incidents=resolved_incidents,
                         pending_incidents=pending_incidents,
                         datetime=datetime)

@app.route('/dashboard')
@login_required
@unit_required
def dashboard():
    random_phrase = random.choice(WATER_PHRASES)
    
    # Get statistics
    if current_user.role == 'Admin':
        total_incidents = Incident.query.count()
        resolved_incidents = Incident.query.filter_by(status='Résolu').count()
        pending_incidents = Incident.query.filter_by(status='En cours').count()
        recent_incidents = Incident.query.order_by(Incident.date_incident.desc()).limit(5).all()
    else:
        total_incidents = Incident.query.filter_by(unit_id=current_user.unit_id).count()
        resolved_incidents = Incident.query.filter_by(unit_id=current_user.unit_id, status='Résolu').count()
        pending_incidents = Incident.query.filter_by(unit_id=current_user.unit_id, status='En cours').count()
        recent_incidents = Incident.query.filter_by(unit_id=current_user.unit_id).order_by(Incident.date_incident.desc()).limit(5).all()
    
    return render_template('main_dashboard.html',
                         phrase=random_phrase,
                         datetime=datetime,
                         total_incidents=total_incidents,
                         resolved_incidents=resolved_incidents,
                         pending_incidents=pending_incidents,
                         recent_incidents=recent_incidents)

@app.route('/services')
@login_required
@unit_required
def services():
    return render_template('services.html')

@app.route('/listes_dashboard')
@login_required
@unit_required
def listes_dashboard():
    if current_user.role == 'Admin':
        total_incidents = Incident.query.count()
        resolved_incidents = Incident.query.filter_by(status='Résolu').count()
    else:
        total_incidents = Incident.query.filter_by(unit_id=current_user.unit_id).count()
        resolved_incidents = Incident.query.filter_by(unit_id=current_user.unit_id, status='Résolu').count()

    return render_template('listes_dashboard.html',
                         total_incidents=total_incidents,
                         resolved_incidents=resolved_incidents)

@app.route('/exploitation')
@login_required
@unit_required
def exploitation():
    return render_template('departement/exploitation.html')

@app.route('/departements')
@login_required
@unit_required
def departements():
    return render_template('departement/departement.html')

@app.route('/departements/exploitation/rapports')
@login_required
@unit_required
def rapports():
    # Get the count of incidents (you can modify this based on your needs)
    incidents_count = Incident.query.count()
    return render_template('departement/rapports.html', incidents_count=incidents_count)

@app.route('/departement/statistiques')
@login_required
@unit_required
def statistiques():
    return render_template('departement/statistiques.html', datetime=datetime)

def is_admin():
    return current_user.is_authenticated and current_user.role == 'Admin'

@app.route('/zones')
@login_required
def list_zones():
    zones = Zone.query.all()
    return render_template('admin/zones.html', zones=zones)

@app.route('/centers')
@login_required
def list_centers():
    # If user is admin, show all centers
    if current_user.role == 'Admin':
        centers = Center.query.all()
        zones = Zone.query.all()
    # If user is Unit Officer, show only centers in their unit
    elif current_user.assigned_unit:
        centers = Center.query.filter_by(unit_id=current_user.assigned_unit.id).all()
        zones = []
    else:
        centers = []
        zones = []
    return render_template('admin/centers.html', centers=centers, zones=zones)

@app.route('/zones/create', methods=['POST'])
@login_required
def create_zone():
    if current_user.role != 'Admin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    try:
        zone = Zone(
            code=request.form['code'],
            name=request.form['name'],
            description=request.form['description'],
            address=request.form['address'],
            phone=request.form['phone'],
            email=request.form['email']
        )
        db.session.add(zone)
        db.session.commit()
        flash('Zone créée avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la création de la zone: {str(e)}', 'danger')
    
    return redirect(url_for('list_zones'))

@app.route('/zones/edit/<int:id>', methods=['POST'])
@login_required
def edit_zone(id):
    if current_user.role != 'Admin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    zone = Zone.query.get_or_404(id)
    try:
        zone.code = request.form['code']
        zone.name = request.form['name']
        zone.description = request.form['description']
        zone.address = request.form['address']
        zone.phone = request.form['phone']
        zone.email = request.form['email']
        db.session.commit()
        flash('Zone mise à jour avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la mise à jour de la zone: {str(e)}', 'danger')
    
    return redirect(url_for('list_zones'))

@app.route('/zones/delete/<int:id>', methods=['POST'])
@login_required
def delete_zone(id):
    if current_user.role != 'Admin':
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    try:
        zone = Zone.query.get_or_404(id)
        
        # Delete all units in the zone first
        for unit in zone.units:
            # Delete all centers in each unit
            for center in unit.centers:
                db.session.delete(center)
            db.session.delete(unit)
        
        # Finally delete the zone
        db.session.delete(zone)
        db.session.commit()
        flash('Zone supprimée avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression de la zone: {str(e)}', 'danger')
    
    return redirect(url_for('list_zones'))

@app.route('/centers/create', methods=['POST'])
@login_required
def create_center():
    if current_user.role not in ['Admin', 'Unit Officer']:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    try:
        # If Unit Officer, use their unit_id
        unit_id = current_user.unit_id if current_user.role == 'Unit Officer' else request.form['unit_id']
        
        center = Center(
            name=request.form['name'],
            description=request.form['description'],
            address=request.form['address'],
            phone=request.form['phone'],
            email=request.form['email'],
            unit_id=unit_id
        )
        db.session.add(center)
        db.session.commit()
        flash('Centre créé avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la création du centre: {str(e)}', 'danger')
    
    return redirect(url_for('list_centers'))

@app.route('/centers/edit/<int:id>', methods=['POST'])
@login_required
def edit_center(id):
    center = Center.query.get_or_404(id)
    
    # Check permissions
    if current_user.role == 'Unit Officer' and center.unit_id != current_user.unit_id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    try:
        center.name = request.form['name']
        center.description = request.form['description']
        center.address = request.form['address']
        center.phone = request.form['phone']
        center.email = request.form['email']
        if current_user.role == 'Admin':
            center.unit_id = request.form['unit_id']
        db.session.commit()
        flash('Centre mis à jour avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la mise à jour du centre: {str(e)}', 'danger')
    
    return redirect(url_for('list_centers'))

@app.route('/centers/delete/<int:id>', methods=['POST'])
@login_required
def delete_center(id):
    center = Center.query.get_or_404(id)
    
    # Check permissions
    if current_user.role == 'Unit Officer' and center.unit_id != current_user.unit_id:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('main_dashboard'))
    
    try:
        db.session.delete(center)
        db.session.commit()
        flash('Centre supprimé avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression du centre: {str(e)}', 'danger')
    
    return redirect(url_for('list_centers'))

@app.route('/select-unit', methods=['GET', 'POST'])
@login_required
def select_unit():
    if request.method == 'POST':
        unit_id = request.form.get('unit_id')  # Changed from 'unit' to 'unit_id'
        if unit_id:
            current_user.unit_id = unit_id
            db.session.commit()
            flash('Votre unité a été mise à jour avec succès.', 'success')
            return redirect(url_for('dashboard'))
    
    zones = Zone.query.all()
    return render_template('select_unit.html', zones=zones)

@app.route('/api/units/<int:zone_id>')
@login_required
def get_zone_units(zone_id):
    """Get all units for a specific zone."""
    try:
        units = Unit.query.filter_by(zone_id=zone_id).all()
        return jsonify([{'id': unit.id, 'name': unit.name} for unit in units])
    except Exception as e:
        app.logger.error(f"Error fetching units for zone {zone_id}: {str(e)}")
        return jsonify({'error': 'Error fetching units'}), 500

@app.context_processor
def inject_pending_users_count():
    if current_user.is_authenticated and current_user.role == 'Admin':
        from models import User
        pending_users_count = User.query.filter_by(role='Pending').count()
        return {'pending_users_count': pending_users_count}
    return {'pending_users_count': None}

if __name__ == '__main__':
    # Create default admin user if it doesn't exist
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                role='Admin'
            )
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
    
    print("\n" + "="*50)
    print("Application is running!")
    print("Default admin credentials:")
    print("Username: admin")
    print("Password: admin")
    print("Please change these credentials after first login.")
    print("="*50 + "\n")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
