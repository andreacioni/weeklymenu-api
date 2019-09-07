from .. import mongo

class RecipeIngredient(mongo.EmbeddedDocument):
    quantity = mongo.FloatField()
    required = mongo.BooleanField(required=True, default=True)
    ingredient = mongo.ReferenceField('Ingredient', reverse_delete_rule=mongo.CASCADE)

class Recipe(mongo.Document):
    name = mongo.StringField(required=True, unique=True)
    description = mongo.StringField()
    note = mongo.StringField()
    availabilityMonths = mongo.ListField(mongo.IntField(min_value=1, max_value=12), max_length=12)
    ingredients = mongo.EmbeddedDocumentListField('RecipeIngredient')
    servs = mongo.IntegerField(min_value=1)
    estimatedCookingTime = mongo.IntegerField(min_value=1)
    estimatedPreparationTime = mongo.IntegerField(min_value=1)
    tags = mongo.ListField(
        mongo.StringField()
    )
    
    def __repr__(self):
           return "<Recipe '{}'>".format(self.name)