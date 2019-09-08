from .. import mongo
from ..models import Ingredient

class ShoppingItem(mongo.EmbeddedDocument):
    checked = mongo.BooleanField(required=True, default=False)
    ingredient = mongo.ReferenceField('Ingredient')
    supermarketSection = mongo.StringField()

class ShoppingList(mongo.Document):
    items = mongo.EmbeddedDocumentListField('ShoppingItem')

    def __repr__(self):
           return "<ShoppingList '{}'>".format(self.items)