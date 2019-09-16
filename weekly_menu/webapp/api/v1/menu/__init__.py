from .. import BASE_PATH

def create_module(app, api):
    
    from .resources import MenuList, MenuInstance
    
    api.add_resource(
        MenuList,
        BASE_PATH + '/menus'
    )
    api.add_resource(
        MenuInstance,
        BASE_PATH + '/menus/<string:menu_id>'
    )