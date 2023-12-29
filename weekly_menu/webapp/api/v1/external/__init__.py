def create_module(app, **kwargs):
    from .controllers import external_blueprint
    app.register_blueprint(external_blueprint)
