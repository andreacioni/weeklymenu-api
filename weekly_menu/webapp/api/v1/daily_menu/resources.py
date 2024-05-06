import pprint
import re

from datetime import datetime
from flask import jsonify
from flask_restful import Resource, abort, request, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError
from mongoengine.fields import ObjectIdField, ObjectId
from mongoengine.queryset.visitor import Q

from .schemas import DailyMenuSchema, PatchMenuSchema, PutMenuSchema
from ...models import Ingredient, User, menu, ShoppingList, Menu, Recipe, DailyMenu
from ... import (
    validate_payload,
    paginated,
    mongo,
    load_user_info,
    put_document,
    patch_document,
    parse_query_args,
    search_on_model,
)
from ...exceptions import DuplicateEntry, BadRequest


def _parse_date(date):
    try:
        return datetime.strptime(date, "%Y-%m-%d")
    except ValueError as ex:
        raise BadRequest(
            description="Date must be in the form yyyy-MM-dd",
            details=ex.args or [],
        )


class DailyMenuList(Resource):

    @jwt_required
    @parse_query_args
    @paginated
    @load_user_info
    def get(self, query_args, page_args, user_info: User):
        return search_on_model(
            DailyMenu, Q(owner=str(user_info.id)), query_args, page_args
        )

    @jwt_required
    @validate_payload(DailyMenuSchema(), "menu")
    @load_user_info
    def post(self, menu: Menu, user_info: User):
        # Associate user id
        menu.owner = user_info.id

        try:
            menu.save(force_insert=True)
        except NotUniqueError as nue:
            raise DuplicateEntry(
                description="duplicate entry found for a menu", details=nue.args or []
            )

        return menu, 201


class DailyMenuInstance(Resource):
    @jwt_required
    @load_user_info
    def get(self, user_info: User, day=""):
        searched_day = _parse_date(day)

        menu = DailyMenu.objects(
            Q(owner=str(user_info.id)) & Q(date=searched_day)
        ).get_or_404()
        return menu

    @jwt_required
    @load_user_info
    def delete(self, user_info: User, day=""):
        searched_day = _parse_date(day)

        DailyMenu.objects(
            Q(owner=str(user_info.id)) & Q(date=searched_day)
        ).get_or_404().delete()
        return "", 204

    @jwt_required
    @validate_payload(PutMenuSchema(), "new_menu")
    @load_user_info
    def put(self, new_menu: Ingredient, user_info: User, day=""):
        searched_day = _parse_date(day)

        old_menu = DailyMenu.objects(
            Q(date=searched_day) & Q(owner=str(user_info.id))
        ).get_or_404()

        result = put_document(DailyMenu, new_menu, old_menu)

        if result.modified_count != 1:
            raise BadRequest(
                description="no matching menu for day: {}".format(searched_day)
            )

        old_menu.reload()
        return old_menu, 200

    @jwt_required
    @validate_payload(PatchMenuSchema(), "new_menu")
    @load_user_info
    def patch(self, new_menu: Menu, user_info: User, day=""):
        searched_day = _parse_date(day)

        old_menu = Menu.objects(
            Q(date=searched_day) & Q(owner=str(user_info.id))
        ).get_or_404()

        result = patch_document(Menu, new_menu, old_menu)

        if result.modified_count != 1:
            raise BadRequest(
                description="no matching menu for day: {}".format(searched_day)
            )

        old_menu.reload()
        return old_menu, 200
