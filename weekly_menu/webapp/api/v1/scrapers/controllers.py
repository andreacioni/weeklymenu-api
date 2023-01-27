import logging
import re
from uuid import uuid4
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask_jwt_extended.config import config
from marshmallow_mongoengine import schema

from weekly_menu.webapp.api.models.recipe import Recipe, RecipeIngredient, RecipePreparationStep

from . import scrape_recipe_from_url
from .. import BASE_PATH
from ... import QueryArgs, parse_query_args, validate_payload
from ...models import User, ShoppingList, UserPreferences
from ...exceptions import BadRequest, InvalidCredentials, NotFound, ParseFailed

_logger = logging.getLogger(__name__)

scraper_blueprint = Blueprint(
    'scrapers',
    __name__,
    url_prefix=BASE_PATH + '/scrapers'
)


@scraper_blueprint.route('/recipe')
@jwt_required
@parse_query_args
def scrape_recipe(query_args):
    if (QueryArgs.URL not in query_args or query_args[QueryArgs.URL] == None):
        raise BadRequest('url not provided')

    url = query_args[QueryArgs.URL]

    try:
        recipeRaw = jsonify(scrape_recipe_from_url(url)).json
    except:
        _logger.warn('no recipe found at url {}'.format(url))
        raise NotFound('no recipe found on supplied URL')

    # try:
    recipe = Recipe(
        name=recipeRaw['title'],
        ingredients=list(
            map((lambda i: RecipeIngredient(name=i)), recipeRaw['ingredients'])),
        servs=_extract_number(recipeRaw['servings']),
        imgUrl=recipeRaw['image'],
        preparationSteps=list(map(lambda p: RecipePreparationStep(
            description=p), recipeRaw['instructions_list'])),
        recipeUrl=url,
        scraped=True
    )
    # except:
    #    _logger.exception(
    #        'failed to parse the scraped recipe at {}'.format(recipeRaw))
    #    raise ParseFailed('failed to parse the scraped recipe')

    return recipe.to_mongo(), 200


def _extract_number(s: str):
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    else:
        return None
