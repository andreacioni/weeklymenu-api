import logging
import re
import spacy

from uuid import uuid4
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from flask_jwt_extended.config import config
from marshmallow_mongoengine import schema
from spacy.tokens import Span, Doc

from ...models.recipe import Recipe, RecipeIngredient, RecipePreparationStep
from . import scrape_recipe_from_url
from .. import BASE_PATH
from ... import QueryArgs, parse_query_args, validate_payload
from ...models import User, ShoppingList, UserPreferences
from ...exceptions import BadRequest, InvalidCredentials, NotFound, ParseFailed
from .....lib.ingredients_parser import (
    IngredientParseException,
    IngredientsParserV0,
    IngredientsParserV1,
)
from .....lib.recipe_parser import RecipeParserV0

_logger = logging.getLogger(__name__)

scraper_blueprint = Blueprint("scrapers", __name__, url_prefix=BASE_PATH + "/scrapers")


@scraper_blueprint.route("/recipe")
@jwt_required
@parse_query_args
def scrape_recipe(query_args):
    if QueryArgs.URL not in query_args or query_args[QueryArgs.URL] == None:
        raise BadRequest("url not provided")

    url = query_args[QueryArgs.URL]

    try:
        recipeRaw = jsonify(scrape_recipe_from_url(url)).json
    except:
        _logger.warn("no recipe found at url {}".format(url))
        raise NotFound("no recipe found on supplied URL")

    ingredient_parser_available = [0, 1]
    ingredient_parser_available.remove(query_args[QueryArgs.INGREDIENT_PARSER_VERSION])
    ingredient_parser_available = [
        query_args[QueryArgs.INGREDIENT_PARSER_VERSION]
    ] + ingredient_parser_available

    done = False

    for ing_parser in ingredient_parser_available:
        try:
            parser = RecipeParserV0()
            recipe = parser.from_json(
                recipeRaw,
                url=url,
                model_base_path=current_app.config["MODELS_BASE_PATH"],
                ingredient_parser_version=ing_parser,
            )
            done = True
            break
        except IngredientParseException:
            _logger.warn("failed to parse ingredients in recipe")
        except:
            _logger.exception(
                "failed to parse the scraped recipe at {}".format(recipeRaw)
            )
            raise ParseFailed("failed to parse the scraped recipe")

    if done == False:
        raise ParseFailed(
            "failed to parse the scraped recipe, ingredient parser exhausted"
        )

    return recipe.to_mongo(), 200
