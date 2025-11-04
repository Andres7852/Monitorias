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

    materia = db.relationship('Materia', backref=db.backref('monitorias', lazy=True))
