from .. import mongo

class Menu(mongo.Document):
    name = mongo.StringField(unique=True, required=True)
    date = mongo.DateTimeField(required=True)
    meal = mongo.StringField('Meal')
    recipes = mongo.ListField(
        mongo.ReferenceField('Recipe', reverse_delete_rule=mongo.PULL)
    )
    user = mongo.ReferenceField('User', required=True, reverse_delete_rule=mongo.NULLIFY) #It could be useful to have an history of user's menu also when they leave

    def __repr__(self):
           return "<Menu '{}'>".format(self.name)