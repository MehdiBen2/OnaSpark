from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from urllib.parse import urlparse
import random
from models import User, db

# Create the blueprint
auth = Blueprint('auth', __name__)

# Water and sanitation phrases
WATER_PHRASES = [
    "L'eau est l'essence de la vie ; préservons-la pour les générations futures.",
    "L'assainissement est une question de dignité ; assurons-le pour tous.",
    "Chaque goutte compte ; économisez l'eau dès aujourd'hui.",
    "De l'eau propre, des vies saines.",
    "Un bon assainissement prévient les maladies ; c'est notre responsabilité partagée.",
    "L'accès à l'eau potable est un droit humain.",
    "L'assainissement est la clé d'un avenir durable.",
    "L'eau soutient la vie ; gardons-la propre.",
    "L'hygiène, c'est la santé ; priorisons l'assainissement.",
    "Ensemble, nous pouvons rendre l'eau potable et l'assainissement accessibles à tous."
]

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if current_user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': True, 'redirect': url_for('main_dashboard')}
        return redirect(url_for('main_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main_dashboard')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {'success': True, 'redirect': next_page}
            
            flash('Connexion réussie!', 'success')
            return redirect(next_page)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {'success': False, 'message': 'Nom d\'utilisateur ou mot de passe incorrect.'}
            
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    
    # Get a random water phrase
    random_phrase = random.choice(WATER_PHRASES)
    return render_template('login.html', water_phrase=random_phrase)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_dashboard'))
    
    if request.method == 'GET':
        random_phrase = random.choice(WATER_PHRASES)
        return render_template('register.html', water_phrase=random_phrase)
    
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validate input
        errors = {}
        if not username or len(username) < 3:
            errors['username'] = 'Le nom d\'utilisateur doit contenir au moins 3 caractères'
        if not email or '@' not in email:
            errors['email'] = 'Email invalide'
        if not password or len(password) < 6:
            errors['password'] = 'Le mot de passe doit contenir au moins 6 caractères'
            
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            errors['username'] = 'Ce nom d\'utilisateur existe déjà'
        if User.query.filter_by(email=email).first():
            errors['email'] = 'Cet email est déjà utilisé'
            
        if errors:
            return {'success': False, 'errors': errors}, 400
            
        # Create pending user
        try:
            new_user = User(
                username=username,
                email=email,
                role='Pending',
                is_active=False
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Votre demande a été envoyée avec succès. L\'administrateur examinera votre demande.'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Une erreur est survenue lors de l\'inscription. Veuillez réessayer.'
            }, 500

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
