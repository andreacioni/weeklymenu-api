from .. import BASE_PATH

def create_module(app, api):
    
    from .resources import ShoppingListResource, ShoppingListItemsResource
    
    api.add_resource(
        ShoppingListResource,
        BASE_PATH + '/shopping-list/<string:shopping_list_id>'
    )

    api.add_resource(
        ShoppingListItemsResource,
        BASE_PATH + '/shopping-list/<string:shopping_list_id>/items'
    )