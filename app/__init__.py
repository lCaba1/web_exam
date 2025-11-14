import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()

migrate = Migrate()

login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
login.login_message_category = 'warning'

@login.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)

    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.py')
    app.config.from_pyfile(config_path)
    
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.views import main_bp
    app.register_blueprint(main_bp)

    from app.views import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app