from .. import mongo

from .base_document import BaseDocument


class DailyMenuMeal(mongo.EmbeddedDocument):
    recipes = mongo.ListField(
        # reverse_delete_rule=mongo.PULL not allowed (https://github.com/MongoEngine/mongoengine/issues/1592)
        mongo.ReferenceField("Recipe"),
        default=None,
    )


class DailyMenu(BaseDocument):
    date = mongo.DateField(required=True)

    meals = mongo.MapField(mongo.EmbeddedDocumentField(DailyMenuMeal), default={})

    meta = {
        "collection": "daily_menu",
        "indexes": [{"fields": ["owner", "-date"], "unique": True}],
    }

    def __repr__(self):
        return "<DailyMenu '{}'>".format(self.date)
