from .. import BASE_PATH

def create_module(app, api):
    
    from .resources import RecipeList, RecipeInstance
    
    api.add_resource(
        RecipeList,
        BASE_PATH + '/recipes'
    )
    api.add_resource(
        RecipeInstance,
        BASE_PATH + '/recipes/<string:reciper_id>'
    )