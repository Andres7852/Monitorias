from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models import db, User
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

# códigos de ejemplo (modifica según necesites)
VALID_PROF_CODES = {'PROF2024A', 'PROF2024B'}
VALID_DEC_CODES = {'DEC2024X'}

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'estudiante':
            return redirect(url_for('estudiante.dashboard'))
        if current_user.role == 'profesor':
            return redirect(url_for('profesor.dashboard'))
        if current_user.role == 'decano':
            return redirect(url_for('decano.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Bienvenido ' + user.nombre)
            if user.role == 'estudiante':
                return redirect(url_for('estudiante.dashboard'))
            if user.role == 'profesor':
                return redirect(url_for('profesor.dashboard'))
            if user.role == 'decano':
                return redirect(url_for('decano.dashboard'))
        flash('Correo o contraseña incorrectos')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        carrera = request.form.get('carrera') if role == 'estudiante' else None
        semestre = int(request.form.get('semestre')) if (role == 'estudiante' and request.form.get('semestre')) else None
        access_code = request.form.get('access_code', '').strip() or None

        if User.query.filter_by(email=email).first():
            flash('El correo ya está registrado')
            return redirect(url_for('auth.register'))

        # validar códigos si rol profesor o decano
        if role == 'profesor' and access_code not in VALID_PROF_CODES:
            flash('Código de profesor inválido o ausente')
            return redirect(url_for('auth.register'))
        if role == 'decano' and access_code not in VALID_DEC_CODES:
            flash('Código de decano inválido o ausente')
            return redirect(url_for('auth.register'))

        u = User(nombre=nombre, email=email, role=role, carrera=carrera, semestre=semestre, access_code=access_code)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash('Cuenta creada. Inicia sesión.')
        return redirect(url_for('auth.login'))

    carreras = ['Ingeniería de Sistemas','Ingeniería Industrial','Ingeniería Civil','Ingeniería Electrónica','Ingeniería Ambiental','Ingeniería Biomédica','Ingeniería Energética']
    return render_template('register.html', carreras=carreras)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada')
    return redirect(url_for('auth.login'))
