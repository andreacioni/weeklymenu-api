#!/usr/bin/env python3

import certifi
import logging

from os import getenv

from mongoengine import *

from weekly_menu.webapp.api.models.recipe import Recipe
from weekly_menu.lib.recipe_parser import RecipeParserV0, IngredientParseException

from weekly_menu.webapp.api.models.recipe import ExternalRecipe

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

connect(
    host=getenv("JOB_DB_URL"),
    tlsCAFile=certifi.where(),
)

db = get_db()

scraped_recipes_to_import = db.get_collection("scraped_recipes_to_import")

recipe_parser = RecipeParserV0()

ingredient_parser_version = 1
for scraped_recipe in scraped_recipes_to_import.find():
    try:
        recipe = recipe_parser.from_json(
            scraped_recipe,
            url=scraped_recipe.get("canonical_url"),
            ingredient_parser_version=1,
            model_base_path="models/",
        )
        ingredient_parser_version = 1
    except IngredientParseException:
        _logger.warn("failed to parse ingredients of recipe: %s", scraped_recipe["_id"])
        ingredient_parser_version = 0
    except:
        _logger.warn("failed to parse recipe: %s", scraped_recipe["_id"])
        ingredient_parser_version = 1

    try:
        external_recipe = ExternalRecipe.from_json(recipe.to_json())
        external_recipe.scrape_id = scraped_recipe["_id"]
    except Exception as e:
        _logger.error("failed to convert from recipe to external recipe", exc_info=1)
        raise e

    try:
        external_recipe.save()
        _logger.info(
            "saved external recipe: %s into: %s",
            scraped_recipe["_id"],
            external_recipe.id,
        )
    except:
        _logger.error(
            "failed to save external recipe: %s", scraped_recipe["_id"], exc_info=1
        )


disconnect()
