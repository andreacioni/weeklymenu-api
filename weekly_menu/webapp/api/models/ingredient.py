from .. import mongo

class Ingredient(mongo.EmbeddedDocument):
    name = mongo.StringField(required=True, unique=True)
    description = mongo.StringField()
    node = mongo.StringField()
    freezed: mongo.BooleanField()
    availabilityMonths = mongo.ListField(
        mongo.IntField(min_value=1, max_value=12), max_length=12
    )
    tags = mongo.ListField(
        mongo.StringField()
    )

    def __repr__(self):
           return "<Ingredient '{}'>".format(self.name)