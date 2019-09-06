from .. import mongo
from ..models import Ingredient

class ShoppingItem(mongo.EmbeddedDocument):
    checked = mongo.BooleanField(required=True, default=False)
    ingredient = mongo.ReferenceField('Ingredient')

class ShoppingList(mongo.Document):
    items = mongo.ListField(
        mongo.ReferenceField('ShoppingItem')
    )

    def __repr__(self):
           return "<ShoppingList '{}'>".format(self.items)