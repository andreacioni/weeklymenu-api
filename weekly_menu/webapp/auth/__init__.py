from flask_jwt_extended import JWTManager

jwt = JWTManager()

def create_module(app, **kwargs):
    jwt.init_app(app)

def authenticate(username, password):
    from ..models import User
    user = User.query.filter_by(username=username).first()
    if not user:
        return None
    # Do the passwords match
    if not user.check_password(password):
        return None
    return user