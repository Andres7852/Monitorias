from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from .user import User
from .materia import Materia
from .monitoria import Monitoria
from .postulacion import Postulacion
from .asistencia import Asistencia
