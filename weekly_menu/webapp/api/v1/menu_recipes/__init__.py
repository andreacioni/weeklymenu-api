from .. import BASE_PATH

def create_module(app, api):
    
    from .resources import MenuRecipeList, MenuRecipesInstance
    
    api.add_resource(
        MenuRecipesList,
        BASE_PATH + '/menu/<string:menu_id>/recipes'
    )
    api.add_resource(
        MenuRecipesInstance,
        BASE_PATH + '/menu/<string:menu_id>/recipes/<string:recipe_id>'
    )