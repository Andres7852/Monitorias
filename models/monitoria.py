from . import db

class Monitoria(db.Model):
    __tablename__ = 'monitorias'
    id = db.Column(db.Integer, primary_key=True)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)
    titulo = db.Column(db.String(250))
    profesor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    monitor_estudiante_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    horas_requeridas = db.Column(db.Integer, default=20)
    horas_completadas = db.Column(db.Integer, default=0)
    activa = db.Column(db.Boolean, default=False)
    doc_filename = db.Column(db.String(250))  # pdf uploaded for request

    # Relaciones
    materia = db.relationship('Materia', backref=db.backref('monitorias', lazy=True))
    profesor = db.relationship('User', foreign_keys=[profesor_id], backref=db.backref('monitorias_profesor', lazy=True))
    monitor = db.relationship('User', foreign_keys=[monitor_estudiante_id], backref=db.backref('monitorias_monitor', lazy=True))