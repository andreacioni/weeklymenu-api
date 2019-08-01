from .. import BASE_PATH

def create_module(app, api):
    
    from .resources import Ingredients
    
    api.add_resource(
        Ingredients,
        BASE_PATH + '/ingredients'
    )