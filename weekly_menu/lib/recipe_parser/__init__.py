from abc import ABC, abstractmethod
import logging
import re

from ..ingredients_parser import IngredientParseException, from_version
from ...webapp.api.models.recipe import Recipe, BaseRecipe, RecipePreparationStep

_logger = logging.getLogger(__name__)


class RecipeParserInterface(ABC):
    @abstractmethod
    def from_json(self, json_data) -> BaseRecipe:
        raise NotImplemented("from_json is not implemented")


class RecipeParserV0(RecipeParserInterface):
    def from_json(self, json_data, **kwargs) -> BaseRecipe:
        ingredient_parser_version = (
            0
            if kwargs.get("ingredient_parser_version") == None
            else kwargs.get("ingredient_parser_version")
        )

        ingredients = (
            json_data.get("ingredients") if json_data.get("ingredients") != None else []
        )

        try:
            ingredient_parser = from_version(ingredient_parser_version, **kwargs)
            ingredients = ingredient_parser.from_text(json_data.get("ingredients"))
        except:
            _logger.exception(
                "failed to parse ingredient list %s with ingredient parser version: %d",
                json_data.get("ingredients"),
                ingredient_parser_version,
            )
            raise IngredientParseException(
                "failed to parse ingredient list %s with ingredient parser version: %s".format(
                    json_data.get("ingredients"), ingredient_parser_version
                )
            )

        instruction_list = (
            json_data.get("instructions_list")
            if json_data.get("instructions_list") != None
            else []
        )

        return BaseRecipe(
            name=json_data.get("title"),
            ingredients=ingredients,
            servs=self._extract_int(json_data.get("servings")),
            imgUrl=json_data.get("image"),
            preparationSteps=list(
                map(
                    lambda p: RecipePreparationStep(description=p),
                    instruction_list,
                )
            ),
            recipeUrl=kwargs.get("url"),
            scraped=True,
        )

    def _extract_int(self, s: str):
        if s is None or s is not str:
            return None

        match = re.search(r"\d+", s)
        if match:
            return int(match.group())
        else:
            return None
