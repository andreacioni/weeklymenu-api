from .. import mongo

class User(mongo.Document):
    username = mongo.StringField(unique=True, min_length=4, max_length=64)
    password = mongo.BinaryField(required=True)
    email = mongo.StringField(unique=True, regex="^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")

    meta = {
        'collection' : 'users'
    }

    def __repr__(self):
           return "<User '{}'>".format(self.username)