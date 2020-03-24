from .. import mongo

class Menu(mongo.Document):
    name = mongo.StringField()
    date = mongo.DateField(required=True)
    meal = mongo.StringField()
    recipes = mongo.ListField(
        mongo.ReferenceField('Recipe', reverse_delete_rule=mongo.PULL), default=None
    )
    owner = mongo.ReferenceField('User', required=True, reverse_delete_rule=mongo.NULLIFY) #It could be useful to have an history of user's menu also when they leave

    meta = {
        'collection' : 'menu'
    }

    def __repr__(self):
           return "<Menu '{}'>".format(self.name)