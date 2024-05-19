import pprint
import re
import logging

from datetime import datetime
from flask import jsonify
from flask_restful import Resource, abort, request, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import NotUniqueError
from pymongo.errors import DuplicateKeyError
from mongoengine.fields import ObjectIdField, ObjectId
from mongoengine.queryset.visitor import Q

from .schemas import DailyMenuSchema, PatchDailyMenuSchema, PutDailyMenuSchema
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

_logger = logging.getLogger(__name__)


def _check_same_day(day, menu):
    if menu.date != None and day != menu.date.strftime("%Y-%m-%d"):
        raise BadRequest(
            "date parameter inside the payload and url params must be the same"
        )


def _patch_daily_menu(new_menu: DailyMenu, user_info: User) -> DailyMenu:
    old_menu = DailyMenu.objects(
        Q(date=new_menu.date) & Q(owner=str(user_info.id))
    ).get_or_404()

    # merge meals from new to old
    merged_meals = {**old_menu.meals, **new_menu.meals}
    new_menu.meals = merged_meals

    result = patch_document(DailyMenu, new_menu, old_menu)

    if result.modified_count != 1:
        raise BadRequest(
            description="no matching daily menu for day: {}".format(new_menu.date)
        )

    old_menu.reload()
    return old_menu


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
    def post(self, menu: DailyMenu, user_info: User):
        # Associate user id
        menu.owner = user_info.id

        ret_code = 201

        try:
            menu.save(force_insert=True)
        except (NotUniqueError, DuplicateKeyError) as nue:
            _logger.debug("not unique daily menu error: %s", nue)
            menu = _patch_daily_menu(menu, user_info)
            ret_code = 200

        return menu, ret_code


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
    @validate_payload(PutDailyMenuSchema(), "new_menu")
    @load_user_info
    def put(self, new_menu: DailyMenu, user_info: User, day=""):
        _check_same_day(day, new_menu)

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
    @validate_payload(PatchDailyMenuSchema(), "new_menu")
    @load_user_info
    def patch(self, new_menu: DailyMenu, user_info: User, day=""):
        _check_same_day(day, new_menu)

        new_menu = _patch_daily_menu(new_menu, user_info)

        return new_menu, 200
