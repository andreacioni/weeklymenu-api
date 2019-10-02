from .. import mongo
from ..models import Ingredient

class ShoppingListItem(mongo.EmbeddedDocument):
    checked = mongo.BooleanField(required=True, default=False)
    ingredient = mongo.ReferenceField('Ingredient')
    supermarketSection = mongo.StringField()

class ShoppingList(mongo.Document):
    items = mongo.EmbeddedDocumentListField('ShoppingListItem')

    owner = mongo.ReferenceField('User', required=True)

    def __repr__(self):
           return "<ShoppingList '{}'>".format(self.items)