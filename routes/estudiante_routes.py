from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from models import db, Monitoria, Postulacion, Asistencia, Materia
import os
from werkzeug.utils import secure_filename

estudiante_bp = Blueprint('estudiante', __name__, url_prefix='/estudiante')

ALLOWED_CV = {'pdf'}
ALLOWED_CEDULA = {'pdf','png'}
ALLOWED_PHOTO = {'png','jpg','jpeg'}

@estudiante_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'estudiante':
        return redirect(url_for('auth.login'))
    monitorias_activas = Monitoria.query.filter_by(activa=True).all()
    postulaciones = Postulacion.query.filter_by(estudiante_id=current_user.id).all()
    mis_monitorias = Monitoria.query.filter_by(monitor_estudiante_id=current_user.id).all()
    return render_template('dashboard_estudiante.html', monitorias_activas=monitorias_activas, postulaciones=postulaciones, mis_monitorias=mis_monitorias)

@estudiante_bp.route('/postular/<int:monitoria_id>', methods=['GET','POST'])
@login_required
def postular(monitoria_id):
    if current_user.role != 'estudiante':
        return redirect(url_for('auth.login'))
    m = Monitoria.query.get_or_404(monitoria_id)
    if request.method == 'POST':
        cv = request.files.get('cv')
        cedula = request.files.get('cedula')
        photo = request.files.get('photo')
        if not (cv and cedula and photo):
            flash('Debe subir CV (PDF), cédula (PDF o PNG) y foto tipo documento (PNG/JPG).')
            return redirect(request.url)
        if cv.filename.rsplit('.',1)[1].lower() not in ALLOWED_CV or cedula.filename.rsplit('.',1)[1].lower() not in ALLOWED_CEDULA or photo.filename.rsplit('.',1)[1].lower() not in ALLOWED_PHOTO:
            flash('Tipos de archivo incorrectos: CV=PDF, Cédula=PDF/PNG, Foto=PNG/JPG.')
            return redirect(request.url)
        up = current_app.config['UPLOAD_FOLDER']
        os.makedirs(up, exist_ok=True)
        cv_fn = secure_filename(f"{current_user.id}_cv_{monitoria_id}.pdf")
        ced_fn = secure_filename(f"{current_user.id}_ced_{monitoria_id}.{cedula.filename.rsplit('.',1)[1].lower()}")
        photo_fn = secure_filename(f"{current_user.id}_photo_{monitoria_id}.{photo.filename.rsplit('.',1)[1].lower()}")
        cv.save(os.path.join(up, cv_fn))
        cedula.save(os.path.join(up, ced_fn))
        photo.save(os.path.join(up, photo_fn))
        p = Postulacion(estudiante_id=current_user.id, monitoria_id=monitoria_id, cv_filename=cv_fn, cedula_filename=ced_fn, photo_filename=photo_fn)
        db.session.add(p)
        db.session.commit()
        flash('Postulación enviada.')
        return redirect(url_for('estudiante.dashboard'))
    return render_template('postular.html', monitoria=m)

@estudiante_bp.route('/mis_monitorias/upload_asistencia/<int:monitoria_id>', methods=['POST'])
@login_required
def upload_asistencia(monitoria_id):
    if current_user.role != 'estudiante':
        return redirect(url_for('auth.login'))
    f = request.files.get('asistencia')
    if not f:
        flash('Sube la lista de asistencias.')
        return redirect(url_for('estudiante.dashboard'))
    up = current_app.config['UPLOAD_FOLDER']
    os.makedirs(up, exist_ok=True)
    fn = secure_filename(f"{current_user.id}_asistencia_{monitoria_id}_{f.filename}")
    f.save(os.path.join(up, fn))
    a = Asistencia(monitoria_id=monitoria_id, archivo=fn)
    db.session.add(a)
    monitoria = Monitoria.query.get(monitoria_id)
    monitoria.horas_completadas = (monitoria.horas_completadas or 0) + 1
    db.session.commit()
    flash('Lista subida y horas actualizadas.')
    return redirect(url_for('estudiante.dashboard'))

@estudiante_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    up = current_app.config.get('UPLOAD_FOLDER') or 'uploads'
    return send_from_directory(up, filename)
