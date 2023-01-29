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

    try:
        recipe = Recipe(
            name=recipeRaw['title'],
            ingredients=_parse_ingredients(
                recipeRaw['ingredients'], parser_version=query_args[QueryArgs.INGREDIENT_PARSER_VERSION]),
            servs=_extract_int(recipeRaw['servings']),
            imgUrl=recipeRaw['image'],
            preparationSteps=list(map(lambda p: RecipePreparationStep(
                description=p), recipeRaw['instructions_list'])),
            recipeUrl=url,
            scraped=True
        )
    except:
        _logger.exception(
            'failed to parse the scraped recipe at {}'.format(recipeRaw))
        raise ParseFailed('failed to parse the scraped recipe')

    return recipe.to_mongo(), 200


def _parse_ingredients(texts: list, parser_version: int) -> list:
    _logger.info("parser version %d start parsing list: %s",
                 parser_version, texts)
    results = []

    def _v0_parser():
        return list(
            map((lambda i: RecipeIngredient(name=i)), texts))

    def _v1_parser():
        model_base_path = current_app.config['MODELS_BASE_PATH']
        nlp = spacy.load(model_base_path + "/ingredient_parser_model_v1")

        docs = list(nlp.pipe(texts))

        for doc in docs:
            # even if the ingredients belong at the same recipe
            # they are treated as different documents
            try:
                results.append(_recipe_ingredient_from_doc(doc))
            except:
                _logger.exception(
                    "failed to parse ingredient '%s' with v1 parser", doc)

        return results

    try:
        if (parser_version == 1):
            results = _v1_parser()
        else:
            results = _v0_parser()
    except:
        _logger.exception("failed to parse ingredients")

        try:
            results = _v0_parser()
        except:
            _logger.exception(
                "failed to parse ingredients using default parser!")
            results = []

    _logger.info("parser version %d end parsing list: %s (output: %s)",
                 parser_version, texts, results)

    return results


def _recipe_ingredient_from_doc(doc: Doc) -> RecipeIngredient:
    # name is required we must be sure to have it set
    recipeIng = RecipeIngredient(name=doc.text)

    for span in doc.ents:
        # _ent_type could be just
        # - INGREDIENT
        # - QUANTITY
        # - UNIT
        ent_type = doc[span.start].ent_type_

        if (ent_type == "INGREDIENT"):
            recipeIng.name = span.text
        elif (ent_type == "QUANTITY"):
            recipeIng.quantity = _extract_float(span.text)
        elif (ent_type == "UNIT"):
            recipeIng.unitOfMeasure = span.text
        else:
            _logger.error("unexpected ent_type: %s", ent_type)

    return recipeIng


def _extract_int(s: str):
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    else:
        return None


def _extract_float(s: str):
    match = re.search(r'\d+', s)
    if match:
        return float(match.group())
    else:
        return None
