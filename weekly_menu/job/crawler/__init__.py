from mongoengine import *


class RecipeSites(Document):
    name = StringField()
    url = StringField()
    start_urls = ListField()
    enabled = BooleanField()
    search_path = ListField()
    depth = IntField()
    cookies_enabled = BooleanField()
    random_delay_sec = IntField()
    crawler_type = StringField()
    required_recipe_fields = ListField()
