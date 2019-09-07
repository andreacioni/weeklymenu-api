from .. import mongo
from ..models import Ingredient

class ShoppingItem(mongo.EmbeddedDocument):
    checked = mongo.BooleanField(required=True, default=False)
    ingredient = mongo.ReferenceField('Ingredient', reverse_delete_rule=mongo.CASCADE)
    supermarketSection = mongo.StringField()

class ShoppingList(mongo.Document):
    items = mongo.EmbeddedDocumentListField('ShoppingItem')

    def __repr__(self):
           return "<ShoppingList '{}'>".format(self.items)