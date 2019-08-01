from .. import mongo

class Meal(mongo.Document):
    name = mongo.StringField(required=True)

    def __repr__(self):
           return "<Meal '{}'>".format(self.name)