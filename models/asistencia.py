from . import db
import datetime

class Asistencia(db.Model):
    __tablename__ = 'asistencias'
    id = db.Column(db.Integer, primary_key=True)
    monitoria_id = db.Column(db.Integer, db.ForeignKey('monitorias.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=datetime.date.today)
    fecha_subida = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)  # NUEVO CAMPO
    archivo = db.Column(db.String(250))  # filename uploaded
    notas = db.Column(db.String(250))
    monitoria = db.relationship('Monitoria', backref=db.backref('asistencias', lazy=True))