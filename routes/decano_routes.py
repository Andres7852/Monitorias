from models import Monitoria, User
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from models import db, Monitoria, Materia, Postulacion
import os

decano_bp = Blueprint('decano', __name__, url_prefix='/decano')

@decano_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'decano':
        return redirect(url_for('auth.login'))
    
    # Obtener solicitudes pendientes con información del profesor
    pendientes = Monitoria.query.filter_by(activa=False).all()
    for p in pendientes:
        p.profesor = User.query.get(p.profesor_id)
    
    # Obtener monitorías activas con información del profesor y monitor
    monitorias_activas = Monitoria.query.filter_by(activa=True).all()
    for m in monitorias_activas:
        m.profesor = User.query.get(m.profesor_id)
        if m.monitor_estudiante_id:
            m.monitor = User.query.get(m.monitor_estudiante_id)
        else:
            m.monitor = None
    
    return render_template('dashboard_decano.html', pendientes=pendientes, monitorias_activas=monitorias_activas)

@decano_bp.route('/solicitud/<int:id>/decidir/<accion>', methods=['POST'])
@login_required
def decidir(id, accion):
    if current_user.role != 'decano':
        return redirect(url_for('auth.login'))
    m = Monitoria.query.get_or_404(id)
    if accion == 'aceptar':
        if m.activa:
            flash('Esta monitoría ya está activa.')
            return redirect(url_for('decano.dashboard'))
        m.activa = True
        db.session.commit()
        flash('Monitoría activada.')
    else:
        if m.activa:
            flash('No se puede rechazar: la monitoría ya está activa.')
            return redirect(url_for('decano.dashboard'))
        db.session.delete(m)
        db.session.commit()
        flash('Monitoría rechazada y eliminada.')
    return redirect(url_for('decano.dashboard'))

@decano_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    up = current_app.config.get('UPLOAD_FOLDER') or 'uploads'
    return send_from_directory(up, filename)


@decano_bp.route('/ver_asistencias/<int:monitoria_id>')
@login_required
def ver_asistencias_dec(monitoria_id):
    if current_user.role != 'decano':
        flash('Acceso denegado. Solo decanos pueden ver esta sección.')
        return redirect(url_for('auth.login'))
    
    # Obtener la monitoría con el monitor
    from models.asistencia import Asistencia
    monitoria = Monitoria.query.get_or_404(monitoria_id)
    
    # Obtener el nombre del monitor si existe
    if monitoria.monitor_estudiante_id:
        monitor = User.query.get(monitoria.monitor_estudiante_id)
        monitoria.monitor = monitor
    else:
        monitoria.monitor = None
    
    # Obtener asistencias ordenadas por fecha de subida (más recientes primero)
    asistencias = Asistencia.query.filter_by(monitoria_id=monitoria_id).order_by(Asistencia.fecha_subida.desc()).all()
    
    return render_template('ver_asistencias.html', monitoria=monitoria, asistencias=asistencias)