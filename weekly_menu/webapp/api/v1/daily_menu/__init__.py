from .. import BASE_PATH


def create_module(app, api):

    from .resources import DailyMenuList, DailyMenuInstance

    api.add_resource(DailyMenuList, BASE_PATH + "/daily_menu/")
    api.add_resource(DailyMenuInstance, BASE_PATH + "/daily_menu/<string:day>")
