import datetime

from .. import mongo

from .base_document import BaseDocument


class RecipeIngredient(mongo.EmbeddedDocument):
    quantity = mongo.FloatField()
    unitOfMeasure = mongo.StringField(max_length=10)
    required = mongo.BooleanField()
    freezed = mongo.BooleanField()
    ingredient = mongo.ReferenceField("Ingredient")
    name = mongo.StringField(required=True)

    meta = {"strict": False}


class RecipePreparationStep(mongo.EmbeddedDocument):
    description = mongo.StringField(max_length=1000)

    meta = {"strict": False}


class RelatedRecipe(mongo.EmbeddedDocument):
    id = mongo.ObjectIdField()

    meta = {"strict": False}


class BaseRecipe(mongo.Document):
    name = mongo.StringField(required=True)
    description = mongo.StringField()
    preparation = mongo.StringField()  # TODO will be a list of strings
    preparationSteps = mongo.EmbeddedDocumentListField(
        "RecipePreparationStep", default=None
    )
    note = mongo.StringField()
    availabilityMonths = mongo.ListField(
        mongo.IntField(min_value=1, max_value=12), max_length=12, default=None
    )
    ingredients = mongo.EmbeddedDocumentListField("RecipeIngredient", default=None)
    servs = mongo.IntField(min_value=1)
    estimatedCookingTime = mongo.IntField(min_value=1)
    estimatedPreparationTime = mongo.IntField(min_value=1)
    rating = mongo.IntField(min_value=1, max_value=3)
    cost = mongo.IntField(min_value=1, max_value=3)
    difficulty = mongo.StringField()
    recipeUrl = mongo.StringField()
    imgUrl = mongo.StringField()
    videoUrl = mongo.StringField()
    section = mongo.StringField()
    relatedRecipes = mongo.EmbeddedDocumentListField("RelatedRecipe", default=None)
    tags = mongo.ListField(mongo.StringField(), default=None)

    scraped = mongo.BooleanField()
    scraped_at = mongo.DateTimeField(default=datetime.datetime.utcnow)

    meta = {"abstract": True}

    def __repr__(self):
        return "<BaseRecipe '{}'>".format(self.name)


class Recipe(BaseRecipe, BaseDocument):
    meta = {"collection": "recipes", "allow_inheritance": True}

    def __repr__(self):
        return "<Recipe '{}'>".format(self.name)


class IngredientGroup(mongo.EmbeddedDocument):
    purpose = mongo.StringField()
    ingredients = mongo.ListField()


class ScrapedRecipes(mongo.Document):
    # from recipe_scrapers
    host = mongo.StringField()
    title = mongo.StringField(unique_with="host")
    total_time = mongo.IntField()
    image = mongo.StringField()
    ingredients = mongo.ListField()
    ingredient_groups = mongo.EmbeddedDocumentListField(IngredientGroup)
    instructions = mongo.StringField()
    instructions_list = mongo.ListField()
    links = mongo.ListField()
    servings = mongo.IntField()
    nutrients = mongo.DictField()
    canonical_url = mongo.StringField()

    # from scrapy
    url = mongo.StringField()

    meta = {"allow_inheritance": True}


class ExternalRecipe(BaseRecipe):
    scrape_id = mongo.ReferenceField(ScrapedRecipes, reverse_delete_rule=mongo.NULLIFY)

    meta = {"collection": "external_recipes"}

    def __repr__(self):
        return "<ExternalRecipe '{}'>".format(self.name)
