from .. import mongo

class Ingredient(mongo.Document):
    name = mongo.StringField(required=True, unique=True)
    description = mongo.StringField()
    note = mongo.StringField()
    freezed = mongo.BooleanField(default=False)
    availabilityMonths = mongo.ListField(
        mongo.IntField(min_value=1, max_value=12), max_length=12
    )
    tags = mongo.ListField(
        mongo.StringField()
    )
    
    owner = mongo.ReferenceField('User', required=True)

    meta = {
        'collection' : 'ingredients'
    }

    def __repr__(self):
           return "<Ingredient '{}'>".format(self.name)