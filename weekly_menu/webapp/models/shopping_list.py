from .. import mongo

class ShoppingList(mongo.Document):
    items = mongo.ListField(
        mongo.ReferenceField('CheckableIngredient')
    )

    def __repr__(self):
           return "<ShoppingList '{}'>".format(self.items)