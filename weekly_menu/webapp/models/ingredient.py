from .. import mongo

class Ingredient(mongo.Document):
    name = mongo.StringField(required=True)
    description = mongo.StringField()
    node = mongo.StringField()
    availabilityMonths = mongo.ListField(mongo.IntField(min_value=1, max_value=12), max_length=12)
    tags = mongo.ListField(
        mongo.ReferenceField('Tag')
    )


    def __repr__(self):
           return "<Ingredient '{}'>".format(self.name)