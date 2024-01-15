from .. import mongo
from .base_document import BaseDocument

ISO_639_REGEXP = r"^[a-zA-Z]{2,3}$"
ISO_639_MAX_LENGTH = 3


class SupermarketSection(mongo.EmbeddedDocument):
    MAX_SECTION_NAME_LENGTH = 50

    name = mongo.StringField(max_length=MAX_SECTION_NAME_LENGTH, required=True)
    color = mongo.IntField(max_length=MAX_SECTION_NAME_LENGTH)

    meta = {"strict": False}


class UserPreferences(BaseDocument):
    supermarket_sections = mongo.EmbeddedDocumentListField(
        SupermarketSection, default=None
    )

    shopping_days = mongo.ListField(
        mongo.IntField(min_value=1, max_value=7), default=None
    )
    units_of_measure = mongo.ListField(
        mongo.StringField(min_value=1, max_value=10), default=None
    )

    language = mongo.StringField(
        regex=ISO_639_REGEXP, max_length=ISO_639_MAX_LENGTH, default=None
    )

    meta = {"collection": "user_preferences"}

    def __repr__(self):
        return "<UserPreferences '{}, {}'>".format(
            self.supermarketSections, self.shoppingDays, self.units_of_measure
        )
