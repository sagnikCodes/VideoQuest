from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "deprojectsecretkey"
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:password@localhost/users_db"
    db.init_app(app)
    login_manager.init_app(app)

    from .views import views
    from .auth import auth
    from .api import api
    from .creators import creators

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(creators, url_prefix='/creators')

    from .mysql_models import User

    @login_manager.user_loader
    def load_user(user_id):
        # Load the user object based on the user ID
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
    return app