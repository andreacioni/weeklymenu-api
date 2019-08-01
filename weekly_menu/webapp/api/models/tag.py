from .. import mongo

class Tag(mongo.Document):
    name = mongo.StringField(required=True)

    def __repr__(self):
           return "<Tag '{}'>".format(self.name)