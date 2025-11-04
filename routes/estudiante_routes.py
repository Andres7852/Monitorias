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
    
    # Verificar si el estudiante ya es monitor de alguna monitoría
    es_monitor = Monitoria.query.filter_by(monitor_estudiante_id=current_user.id).first() is not None
    
    # Obtener todas las postulaciones del estudiante
    postulaciones = Postulacion.query.filter_by(estudiante_id=current_user.id).all()
    
    # Obtener IDs de monitorías a las que ya se postuló
    postulaciones_ids = [p.monitoria_id for p in postulaciones]
    
    # Monitorías activas
    monitorias_activas = Monitoria.query.filter_by(activa=True).all()
    
    # Filtrar monitorías: no mostrar aquellas a las que ya se postuló o si ya es monitor
    if es_monitor:
        monitorias_disponibles = []
    else:
        monitorias_disponibles = [m for m in monitorias_activas if m.id not in postulaciones_ids]
    
    mis_monitorias = Monitoria.query.filter_by(monitor_estudiante_id=current_user.id).all()
    
    return render_template('dashboard_estudiante.html', 
                         monitorias_activas=monitorias_disponibles, 
                         postulaciones=postulaciones, 
                         mis_monitorias=mis_monitorias,
                         es_monitor=es_monitor,
                         postulaciones_ids=postulaciones_ids)

@estudiante_bp.route('/postular/<int:monitoria_id>', methods=['GET','POST'])
@login_required
def postular(monitoria_id):
    if current_user.role != 'estudiante':
        flash('Acceso denegado.')
        return redirect(url_for('auth.login'))
    
    m = Monitoria.query.get_or_404(monitoria_id)
    
    # VALIDACIÓN 1: Verificar si ya es monitor de alguna monitoría
    if Monitoria.query.filter_by(monitor_estudiante_id=current_user.id).first():
        flash('❌ No puedes postularte a una monitoría si ya eres monitor de otra.')
        return redirect(url_for('estudiante.dashboard'))
    
    # VALIDACIÓN 2: Verificar si ya se postuló a esta monitoría (sin importar el estado)
    postulacion_existente = Postulacion.query.filter_by(
        estudiante_id=current_user.id, 
        monitoria_id=monitoria_id
    ).first()
    
    if postulacion_existente:
        if postulacion_existente.estado == 'pendiente':
            flash('⏳ Ya tienes una postulación pendiente para esta monitoría.')
        elif postulacion_existente.estado == 'aceptado':
            flash('✅ Ya fuiste aceptado en esta monitoría.')
        elif postulacion_existente.estado == 'rechazado':
            flash('❌ Ya te postulaste anteriormente a esta monitoría y fuiste rechazado. No puedes volver a postularte.')
        return redirect(url_for('estudiante.dashboard'))
    
    # VALIDACIÓN 3: Verificar que la monitoría esté activa
    if not m.activa:
        flash('Esta monitoría no está activa.')
        return redirect(url_for('estudiante.dashboard'))
    
    # VALIDACIÓN 4: Verificar que la monitoría no tenga monitor asignado
    if m.monitor_estudiante_id:
        flash('Esta monitoría ya tiene un monitor asignado.')
        return redirect(url_for('estudiante.dashboard'))
    
    if request.method == 'POST':
        cv = request.files.get('cv')
        cedula = request.files.get('cedula')
        photo = request.files.get('photo')
        
        if not (cv and cedula and photo):
            flash('Debe subir CV (PDF), cédula (PDF o PNG) y foto tipo documento (PNG/JPG).')
            return redirect(request.url)
        
        # Validar extensiones
        try:
            cv_ext = cv.filename.rsplit('.',1)[1].lower()
            cedula_ext = cedula.filename.rsplit('.',1)[1].lower()
            photo_ext = photo.filename.rsplit('.',1)[1].lower()
        except:
            flash('Nombres de archivo inválidos.')
            return redirect(request.url)
        
        if cv_ext not in ALLOWED_CV or cedula_ext not in ALLOWED_CEDULA or photo_ext not in ALLOWED_PHOTO:
            flash('Tipos de archivo incorrectos: CV=PDF, Cédula=PDF/PNG, Foto=PNG/JPG.')
            return redirect(request.url)
        
        up = current_app.config['UPLOAD_FOLDER']
        os.makedirs(up, exist_ok=True)
        
        cv_fn = secure_filename(f"{current_user.id}_cv_{monitoria_id}.pdf")
        ced_fn = secure_filename(f"{current_user.id}_ced_{monitoria_id}.{cedula_ext}")
        photo_fn = secure_filename(f"{current_user.id}_photo_{monitoria_id}.{photo_ext}")
        
        cv.save(os.path.join(up, cv_fn))
        cedula.save(os.path.join(up, ced_fn))
        photo.save(os.path.join(up, photo_fn))
        
        p = Postulacion(
            estudiante_id=current_user.id, 
            monitoria_id=monitoria_id, 
            cv_filename=cv_fn, 
            cedula_filename=ced_fn, 
            photo_filename=photo_fn
        )
        db.session.add(p)
        db.session.commit()
        
        flash('✅ Postulación enviada exitosamente.')
        return redirect(url_for('estudiante.dashboard'))
    
    return render_template('postular.html', monitoria=m)

@estudiante_bp.route('/mis_monitorias/upload_asistencia/<int:monitoria_id>', methods=['POST'])
@login_required
def upload_asistencia(monitoria_id):
    if current_user.role != 'estudiante':
        return redirect(url_for('auth.login'))
    
    # Verificar que el estudiante es el monitor de esta monitoría
    monitoria = Monitoria.query.get_or_404(monitoria_id)
    if monitoria.monitor_estudiante_id != current_user.id:
        flash('No tienes permiso para subir asistencias a esta monitoría.')
        return redirect(url_for('estudiante.dashboard'))
    
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
    
    # CAMBIO: Sumar 2 horas en lugar de 1
    monitoria.horas_completadas = (monitoria.horas_completadas or 0) + 2
    db.session.commit()
    flash('Lista subida exitosamente. Se han añadido 2 horas al progreso.')
    return redirect(url_for('estudiante.dashboard'))

@estudiante_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    up = current_app.config.get('UPLOAD_FOLDER') or 'uploads'
    return send_from_directory(up, filename)