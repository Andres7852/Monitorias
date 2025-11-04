from app import create_app
from models import db, Materia
import os

app = create_app()
with app.app_context():
    os.makedirs(app.instance_path, exist_ok=True)
    db.create_all()

    # seed materias if empty
    if not Materia.query.first():
        materias = ['Matemáticas I','Física I','Programación I','Estructuras de Datos','Bases de Datos',
                    'Ingeniería de Sistemas','Ingeniería Industrial','Ingeniería Civil','Ingeniería Electrónica']
        for m in materias:
            db.session.add(Materia(nombre=m))
        db.session.commit()
    print('Base de datos inicializada en:', os.path.join(app.instance_path, 'monitorias.db'))
