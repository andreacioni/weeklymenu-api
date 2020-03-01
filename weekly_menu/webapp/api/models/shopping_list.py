from .. import mongo
from ..models import Ingredient

class ShoppingListItem(mongo.EmbeddedDocument):
    checked = mongo.BooleanField(required=True)
    item = mongo.ReferenceField('Ingredient', required=True)
    supermarketSection = mongo.StringField()

class ShoppingList(mongo.Document):
    name = mongo.StringField(unique=True)
    items = mongo.EmbeddedDocumentListField('ShoppingListItem', default=None)

    owner = mongo.ReferenceField('User', required=True)

    meta = {
        'collection' : 'shopping_lists'
    }

    def __repr__(self):
           return "<ShoppingList '{}'>".format(self.name)