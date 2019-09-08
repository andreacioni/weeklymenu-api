from .. import mongo

class User(mongo.Document):
    username = mongo.StringField(unique=True, min_length=4, max_length=64)
    password = mongo.BinaryField(required=True)
    email = mongo.StringField(unique=True, regex="^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")

    shoppindDay = mongo.ListField(
        mongo.IntField(min_value=1, max_value=7)
    )

    ingredients_docs = mongo.ListField(
        mongo.ReferenceField('Ingredient', reverse_delete_rule=mongo.PULL)
    )

    recipes_docs = mongo.ListField(
        mongo.ReferenceField('Recipe', reverse_delete_rule=mongo.PULL)
    )

    menu_docs = mongo.ListField(
        mongo.ReferenceField('Menu', reverse_delete_rule=mongo.PULL)
    )

    shopping_list_doc = mongo.ReferenceField('ShoppingList', reverse_delete_rule=mongo.PULL)

    meta = {
        'collection' : 'users'
    }

    def __repr__(self):
           return "<User '{}'>".format(self.username)