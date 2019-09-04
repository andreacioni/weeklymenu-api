from .. import BASE_PATH

def create_module(app, api):
    
    from .resources import UserInstance
    
    api.add_resource(
        UserInstance,
        BASE_PATH + '/users/<string:user_id>'
    )