from . import db

class Postulacion(db.Model):
    __tablename__ = 'postulaciones'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    monitoria_id = db.Column(db.Integer, db.ForeignKey('monitorias.id'), nullable=False)
    cv_filename = db.Column(db.String(250))
    cedula_filename = db.Column(db.String(250))
    photo_filename = db.Column(db.String(250))
    estado = db.Column(db.String(30), default='pendiente')  # pendiente, aceptado, rechazado

    estudiante = db.relationship('User', foreign_keys=[estudiante_id])
    monitoria = db.relationship('Monitoria', foreign_keys=[monitoria_id])
