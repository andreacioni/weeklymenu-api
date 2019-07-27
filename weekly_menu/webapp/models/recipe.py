from .. import mongo

class Recipe(mongo.Document):
    name = mongo.StringField(primary_key=True)
    description = mongo.StringField()
    note = mongo.StringField()
    availabilityMonths = mongo.ListField(mongo.IntField(min_value=1, max_value=12), max_length=12)
    tags = mongo.ListField(
        mongo.ReferenceField('Tag')
    )
    def __repr__(self):
           return "<Recipe '{}'>".format(self.name)