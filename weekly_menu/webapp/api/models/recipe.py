from .. import mongo

class Recipe(mongo.Document):
    name = mongo.StringField(required=True, unique=True)
    description = mongo.StringField()
    note = mongo.StringField()
    availabilityMonths = mongo.ListField(mongo.IntField(min_value=1, max_value=12), max_length=12)
    ingredients = mongo.ListField(
        mongo.ReferenceField('Ingredient')
    )
    tags = mongo.ListField(
        mongo.ReferenceField('Tag')
    )
    def __repr__(self):
           return "<Recipe '{}'>".format(self.name)