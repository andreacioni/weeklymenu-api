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


class IngredientGroup(EmbeddedDocument):
    purpose = StringField()
    ingredients = ListField()


class ScrapedRecipes(Document):
    # from recipe_scrapers
    host = StringField()
    title = StringField(unique_with="host")
    total_time = IntField()
    image = StringField()
    ingredients = ListField()
    ingredient_groups = EmbeddedDocumentListField(IngredientGroup)
    instructions = StringField()
    instructions_list = ListField()
    links = ListField()
    servings = IntField()
    nutrients = DictField()
    canonical_url = StringField()

    # from scrapy
    url = StringField()

    meta = {"allow_inheritance": True}
