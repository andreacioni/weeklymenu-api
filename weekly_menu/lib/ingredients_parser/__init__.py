from abc import ABC, abstractmethod
import logging
import spacy
import re

from spacy.tokens import Span, Doc

from ...webapp.api.models.recipe import Recipe, RecipeIngredient, RecipePreparationStep

_logger = logging.getLogger(__name__)


class IngredientParseException(Exception):
    def __init__(self, message="Failed to parse an ingredient"):
        self.message = message
        super().__init__(self.message)


class IngredientsParserInterface(ABC):
    @abstractmethod
    def from_text(self, text_data: list) -> list:
        raise NotImplemented("from_text is not implemented")


class IngredientsParserV0(IngredientsParserInterface):
    def from_text(self, text_data: list) -> list:
        return list(map((lambda i: RecipeIngredient(name=i)), text_data))


class IngredientsParserV1(IngredientsParserInterface):
    _nlp = None

    def __new__(cls, **kwargs):
        model_base_path = kwargs.get("model_base_path")

        # TODO thread safety needed while initializing nlp
        if IngredientsParserV1._nlp == None:
            IngredientsParserV1._nlp = spacy.load(
                model_base_path + "/ingredient_parser_model_v1"
            )

        return super().__new__(cls)

    def __init__(self, **kwargs):
        self.model_base_path = kwargs["model_base_path"]

    def from_text(self, text_data: list) -> list:
        results = []

        docs = list(IngredientsParserV1._nlp.pipe(text_data))

        for doc in docs:
            # even if the ingredients belong at the same recipe
            # they are treated as different documents
            try:
                results.append(self._recipe_ingredient_from_doc(doc))
            except:
                _logger.exception("failed to parse ingredient '%s' with v1 parser", doc)

        return results

    def _recipe_ingredient_from_doc(self, doc: Doc) -> RecipeIngredient:
        # name is required we must be sure to have it set
        recipeIng = RecipeIngredient(name=doc.text)

        for span in doc.ents:
            # _ent_type could be just
            # - INGREDIENT
            # - QUANTITY
            # - UNIT
            ent_type = doc[span.start].ent_type_

            if ent_type == "INGREDIENT":
                recipeIng.name = span.text
            elif ent_type == "QUANTITY":
                recipeIng.quantity = self._extract_float(span.text)
            elif ent_type == "UNIT":
                recipeIng.unitOfMeasure = span.text
            else:
                _logger.error("unexpected ent_type: %s", ent_type)

        return recipeIng

    def _extract_float(self, s: str):
        match = re.search(r"\d+", s)
        if match:
            return float(match.group())
        else:
            return None


def from_version(parser_version: int, **kwargs) -> IngredientsParserInterface:
    if parser_version == 1:
        return IngredientsParserV1(**kwargs)
    else:
        return IngredientsParserV0()
