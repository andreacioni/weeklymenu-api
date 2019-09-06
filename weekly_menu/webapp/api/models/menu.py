from .. import mongo

class Menu(mongo.Document):
    name = mongo.StringField(unique=True, required=True)
    date = mongo.DateTimeField(required=True)
    meal = mongo.StringField('Meal')
    recipes = mongo.ListField(
        mongo.ReferenceField('Recipe', reverse_delete_rule=4)
    )

    def __repr__(self):
           return "<Menu '{}'>".format(self.name)