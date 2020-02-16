from .. import mongo


class RecipeIngredient(mongo.EmbeddedDocument):
    quantity = mongo.FloatField()
    required = mongo.BooleanField()
    ingredient = mongo.ReferenceField('Ingredient', required=True)


class Recipe(mongo.Document):
    name = mongo.StringField(required=True)
    description = mongo.StringField()
    note = mongo.StringField()
    availabilityMonths = mongo.ListField(mongo.IntField(
        min_value=1, max_value=12), max_length=12, default=None)
    ingredients = mongo.EmbeddedDocumentListField(
        'RecipeIngredient', default=None)
    servs = mongo.IntField(min_value=1)
    estimatedCookingTime = mongo.IntField(min_value=1)
    estimatedPreparationTime = mongo.IntField(min_value=1)
    rating = mongo.IntField(min_value=1, max_value=5)
    recipeUrl = mongo.StringField()
    tags = mongo.ListField(
        mongo.StringField(), default=None
    )

    owner = mongo.ReferenceField('User', required=True)

    meta = {
        'collection': 'recipes'
    }

    def __repr__(self):
        return "<Recipe '{}'>".format(self.name)
