from .. import mongo

class Ingredient(mongo.Document):
    name = mongo.StringField(required=True)
    description = mongo.StringField()
    note = mongo.StringField()
    edible = mongo.BooleanField()
    freezed = mongo.BooleanField()
    availabilityMonths = mongo.ListField(
        mongo.IntField(min_value=1, max_value=12), max_length=12, default=None
    )
    tags = mongo.ListField(
        mongo.StringField(), default=None
    )
    
    owner = mongo.ReferenceField('User', required=True)

    meta = {
        'collection' : 'ingredients'
    }

    def __repr__(self):
           return "<Ingredient '{}'>".format(self.name)