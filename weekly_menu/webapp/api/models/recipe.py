from .. import mongo

class RecipeIngredient(mongo.EmbeddedDocument):
    quantity = mongo.FloatField()
    required = mongo.BooleanField(required=True, default=True)
    ingredient = mongo.ReferenceField('Ingredient')

class Recipe(mongo.Document):
    name = mongo.StringField(required=True, unique=True)
    description = mongo.StringField()
    note = mongo.StringField()
    availabilityMonths = mongo.ListField(mongo.IntField(min_value=1, max_value=12), max_length=12)
    ingredients = mongo.EmbeddedDocumentListField('RecipeIngredient')
    servs = mongo.IntField(min_value=1)
    estimatedCookingTime = mongo.IntField(min_value=1)
    estimatedPreparationTime = mongo.IntField(min_value=1)
    rating = mongo.IntField(min_value=1, max_value=5)
    recipeUrl = mongo.StringField()
    tags = mongo.ListField(
        mongo.StringField()
    )

    owner = mongo.ReferenceField('User', required=True)
    
    def __repr__(self):
           return "<Recipe '{}'>".format(self.name)