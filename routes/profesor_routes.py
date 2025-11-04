from models import Monitoria
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from models import db, Monitoria, Materia, Postulacion, Asistencia, User
import os
from werkzeug.utils import secure_filename

profesor_bp = Blueprint('profesor', __name__, url_prefix='/profesor')
ALLOWED_DOCS = {'pdf'}

@profesor_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'profesor':
        return redirect(url_for('auth.login'))
    # postulaciones pendientes para mis monitorias
    solicitudes = Postulacion.query.join(Monitoria, Postulacion.monitoria_id==Monitoria.id).filter(Monitoria.profesor_id==current_user.id, Postulacion.estado=='pendiente').all()
    mis_solicitudes = Monitoria.query.filter_by(profesor_id=current_user.id, activa=False).all()
    monitorias_activas = Monitoria.query.filter_by(profesor_id=current_user.id, activa=True).all()
    return render_template('dashboard_profesor.html', solicitudes=solicitudes, mis_solicitudes=mis_solicitudes, monitorias_activas=monitorias_activas)

@profesor_bp.route('/crear_solicitud', methods=['GET','POST'])
@login_required
def crear_solicitud():
    if current_user.role != 'profesor':
        return redirect(url_for('auth.login'))
    materias_all = Materia.query.all()
    disponibles = [m for m in materias_all if not Monitoria.query.filter_by(materia_id=m.id, activa=True).first()]
    if request.method == 'POST':
        materia_id = int(request.form.get('materia_id'))
        horas = int(request.form.get('horas'))
        doc = request.files.get('doc')  # pdf
        doc_fn = None
        if doc and doc.filename:
            ext = doc.filename.rsplit('.',1)[-1].lower()
            if ext not in ALLOWED_DOCS:
                flash('El documento debe ser PDF')
                return redirect(request.url)
            up = current_app.config.get('UPLOAD_FOLDER') or 'uploads'
            os.makedirs(up, exist_ok=True)
            doc_fn = secure_filename(f"sol_{current_user.id}_{materia_id}_{doc.filename}")
            doc.save(os.path.join(up, doc_fn))
        titulo = f"Solicitud de monitoría {Materia.query.get(materia_id).nombre}"
        mon = Monitoria(materia_id=materia_id, titulo=titulo, profesor_id=current_user.id, horas_requeridas=horas, activa=False, doc_filename=doc_fn)
        db.session.add(mon)
        db.session.commit()
        flash('Solicitud creada. Espera aprobación del decano.')
        return redirect(url_for('profesor.dashboard'))
    return render_template('crear_solicitud.html', materias=disponibles)

@profesor_bp.route('/monitorias')
@login_required
def monitorias():
    if current_user.role != 'profesor':
        return redirect(url_for('auth.login'))
    monitorias = Monitoria.query.filter_by(profesor_id=current_user.id).all()
    return render_template('profesor_monitorias.html', monitorias=monitorias)

@profesor_bp.route('/monitoria/<int:id>/asistencias')
@login_required
def monitoria_asistencias(id):
    if current_user.role != 'profesor':
        return redirect(url_for('auth.login'))
    monitoria = Monitoria.query.get_or_404(id)
    grouped = {}
    for a in monitoria.asistencias:
        grouped.setdefault(str(a.fecha), []).append(a)
    return render_template('monitoria_asistencias.html', monitoria=monitoria, grouped=grouped)

@profesor_bp.route('/postulacion/<int:id>/decidir/<accion>', methods=['POST'])
@login_required
def decidir_postulacion(id, accion):
    if current_user.role not in ('profesor','decano'):
        return redirect(url_for('auth.login'))
    p = Postulacion.query.get_or_404(id)
    if p.estado != 'pendiente':
        flash('Esta postulación ya fue procesada.')
        return redirect(request.referrer or url_for('profesor.dashboard'))
    if accion == 'aceptar':
        p.estado = 'aceptado'
        m = Monitoria.query.get(p.monitoria_id)
        m.monitor_estudiante_id = p.estudiante_id
        m.activa = True
        db.session.commit()
        flash('Postulación aceptada y monitor asignado.')
    else:
        p.estado = 'rechazado'
        db.session.commit()
        flash('Postulación rechazada.')
    return redirect(request.referrer or url_for('profesor.dashboard'))

@profesor_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    up = current_app.config.get('UPLOAD_FOLDER') or 'uploads'
    return send_from_directory(up, filename)


@profesor_bp.route('/ver_asistencias/<int:monitoria_id>')
@login_required
def ver_asistencias_prof(monitoria_id):
    # vista para profesor ver archivos de asistencias
    from models.asistencia import Asistencia
    monitoria = Monitoria.query.get_or_404(monitoria_id)
    asistencias = Asistencia.query.filter_by(monitoria_id=monitoria_id).order_by(Asistencia.fecha_subida.desc()).all()
    return render_template('ver_asistencias.html', monitoria=monitoria, asistencias=asistencias)

