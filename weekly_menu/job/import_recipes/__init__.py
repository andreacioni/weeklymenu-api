from mongoengine import *

from weekly_menu.webapp.api.models.recipe import BaseRecipe
from weekly_menu.job.crawler import ScrapedRecipes


class ExternalRecipe(BaseRecipe):
    scrape_id = ReferenceField(ScrapedRecipes, reverse_delete_rule=NULLIFY)

    meta = {"collection": "external_recipes"}

    def __repr__(self):
        return "<ExternalRecipe '{}'>".format(self.name)
