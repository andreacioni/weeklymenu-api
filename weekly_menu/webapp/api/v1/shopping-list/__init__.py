from .. import BASE_PATH

def create_module(app, api):
    
    from .resources import ShoppingListResource
    
    api.add_resource(
        ShoppingListResource,
        BASE_PATH + '/shopping-list'
    )