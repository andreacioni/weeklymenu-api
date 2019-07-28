from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

from ..models import User


jwt = JWTManager()
crypt = Bcrypt()

def create_module(app, **kwargs):
    crypt.init_app(app)
    jwt.init_app(app)

    from .controllers import auth_blueprint
    app.register_blueprint(auth_blueprint)

def authenticate(username, password):
    from ..models import User
    user = User.objects(
        username__exact=username
    ).first()
    
    if not user:
        return None
    
    # Do the passwords match
    if not bcrypt.check_password_hash(user.password, password):
        return None
    
    return user