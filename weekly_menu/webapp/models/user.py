from .. import mongo


class User(mongo.Document):
    username = mongo.StringField(primary_key=True)
    password = mongo.StringField(required=True)
    email = mongo.StringField(regex="^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")

    def __repr__(self):
           return "<User '{}'>".format(self.name)