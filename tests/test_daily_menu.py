from mongomock import ObjectId
import pytest

from time import sleep
from datetime import datetime
from uuid import uuid4

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from test_ingredient import create_ingredient, delete_ingredient
from test_recipe import create_recipe


def create_or_merge_daily_menu(client, json, auth_headers):
    return client.post("/api/v1/daily_menu/", json=json, headers=auth_headers)


def replace_daily_menu(client, date, json, auth_headers):
    return client.put(
        "/api/v1/daily_menu/{}".format(date), json=json, headers=auth_headers
    )


def patch_daily_menu(client, date, json, auth_headers):
    return client.patch(
        "/api/v1/daily_menu/{}".format(date), json=json, headers=auth_headers
    )


def delete_daily_menu(client, date, auth_headers):
    return client.delete("/api/v1/daily_menu/{}".format(date), headers=auth_headers)


def put_daily_menu(client, date, json, auth_headers):
    return client.put(
        "/api/v1/daily_menu/{}".format(date), json=json, headers=auth_headers
    )


def get_daily_menu(client, date, auth_headers):
    return client.get("/api/v1/daily_menu/{}".format(date), headers=auth_headers)


def get_all_daily_menus(
    client, auth_headers, page=1, per_page=10, order_by="", desc=False
):
    return client.get(
        "/api/v1/daily_menu/?page={}&per_page={}&order_by={}&desc={}".format(
            page, per_page, order_by, desc
        ),
        headers=auth_headers,
    )


def test_not_authorized(client: FlaskClient):
    response = get_all_daily_menus(client, {})

    assert response.status_code == 401

    response = create_or_merge_daily_menu(client, {}, {})

    assert response.status_code == 401


def test_no_menu_defined(client: FlaskClient, auth_headers):
    response = get_all_daily_menus(client, auth_headers)

    assert response.status_code == 200 and len(response.json["results"]) == 0


def test_create_daily_menu(client: FlaskClient, auth_headers):
    response = get_all_daily_menus(client, auth_headers)

    assert response.status_code == 200 and len(response.json["results"]) == 0

    response = create_or_merge_daily_menu(
        client,
        {
            "date": "2019-09-01",
            "meals": {
                "meal1": {
                    "recipes": [],
                }
            },
        },
        auth_headers,
    )

    assert response.status_code == 201

    response = create_or_merge_daily_menu(
        client,
        {
            "date": "2019-09-01",
            "meals": {"meal2": {"recipes": []}},
        },
        auth_headers,
    )

    assert (
        response.status_code == 200
        and len(response.json["meals"]) == 2
        and response.json["meals"]["meal1"]["recipes"] == []
        and response.json["meals"]["meal2"]["recipes"] == []
    )

    recipe = create_recipe(client, {"name": "Tuna and tomatoes"}, auth_headers).json

    response = create_or_merge_daily_menu(
        client,
        {
            "date": "2019-09-01",
            "meals": {
                "meal1": {
                    "recipes": [recipe["_id"]],
                }
            },
        },
        auth_headers,
    )

    assert (
        response.status_code == 200
        and len(response.json["meals"]) == 2
        and response.json["meals"]["meal1"]["recipes"] == [recipe["_id"]]
        and response.json["meals"]["meal2"]["recipes"] == []
    )


def test_delete_daily_menu(client: FlaskClient, auth_headers):
    response = create_or_merge_daily_menu(
        client, {"date": "2019-09-01", "meals": {}}, auth_headers
    )

    assert response.status_code == 201

    response = delete_daily_menu(client, "2019-09-01", auth_headers)

    assert response.status_code == 204


def test_single_daily_menu_get(client: FlaskClient, auth_headers):
    response = create_or_merge_daily_menu(
        client, {"date": "2019-09-01", "meals": {}}, auth_headers
    )

    assert response.status_code == 201

    response = get_daily_menu(client, "2019-09-01", auth_headers)

    assert response.status_code == 200 and response.json["meals"] == {}


def test_single_daily_menu_put(client: FlaskClient, auth_headers):
    response = create_or_merge_daily_menu(
        client, {"date": "2019-09-01", "meals": {}}, auth_headers
    )

    assert response.status_code == 201

    recipe = create_recipe(client, {"name": "Tuna and tomatoes"}, auth_headers).json

    response = put_daily_menu(
        client,
        "2019-09-01",
        {"date": "2019-09-01", "meals": {"meal1": {"recipes": [recipe["_id"]]}}},
        auth_headers,
    )

    assert response.status_code == 200 and response.json["meals"]["meal1"][
        "recipes"
    ] == [recipe["_id"]]

    response = get_daily_menu(client, "2019-09-01", auth_headers)

    assert response.status_code == 200 and response.json["meals"]["meal1"][
        "recipes"
    ] == [recipe["_id"]]
