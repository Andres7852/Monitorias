import os
from flask import Flask
from flask_login import LoginManager
from models import db, User
from routes.auth_routes import auth_bp
from routes.estudiante_routes import estudiante_bp
from routes.profesor_routes import profesor_bp
from routes.decano_routes import decano_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET', 'cambia_esta_clave_por_una_segura')

    # ensure instance folder and absolute db path
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, 'monitorias.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(estudiante_bp)
    app.register_blueprint(profesor_bp)
    app.register_blueprint(decano_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
