from .. import mongo

class Tag(mongo.Document):
    name = mongo.StringField(primary_key=True)

    def __repr__(self):
           return "<Tag '{}'>".format(self.name)