from .. import API_PREFIX

API_VERSION = 'v1'
BASE_PATH = API_PREFIX + '/' + API_VERSION

def create_module(app, api):
    from .auth import create_module as create_auth_module
    from .ingredients import create_module as create_ingredients_module
    from .menu import create_module as create_menu_module
    from .recipes import create_module as create_recipes_module

    create_auth_module(app)

    create_ingredients_module(app, api)
    create_menu_module(app, api)
    create_recipes_module(app, api)

def mongopage_to_json(pagination):
    from flask import jsonify
    return jsonify({
        "results": pagination.items,
        "pages": pagination.pages
    })