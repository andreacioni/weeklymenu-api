from .. import mongo

class Menu(mongo.Document):
    date = mongo.DateTimeField(required=True)
    meal = mongo.ReferenceField('Meal')
    recipes = mongo.ListField(
        mongo.ReferenceField('Recipe')
    )

    def __repr__(self):
           return "<Tag '{}'>".format(self.name)