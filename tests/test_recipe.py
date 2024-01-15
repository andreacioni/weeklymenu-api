from pydoc import cli
from mongomock import ObjectId
import pytest

from mongoengine import get_db
from time import sleep
from datetime import datetime
from uuid import uuid4

from flask import jsonify
from flask.json import dumps, loads
from flask.testing import FlaskClient

from test_ingredient import create_ingredient, delete_ingredient
from test_users import get_user_profile

from weekly_menu.webapp.api.models import (
    Ingredient,
    Menu,
    Recipe,
    User,
    ShoppingList,
    UserPreferences,
)


def create_recipe(client, json, auth_headers):
    return client.post("/api/v1/recipes", json=json, headers=auth_headers)


def patch_recipe(client, recipe_id, json, auth_headers):
    return client.patch(
        "/api/v1/recipes/{}".format(recipe_id), json=json, headers=auth_headers
    )


def put_recipe(client, recipe_id, json, auth_headers):
    return client.put(
        "/api/v1/recipes/{}".format(recipe_id), json=json, headers=auth_headers
    )


def replace_recipe(client, recipe_id, json, auth_headers):
    return client.put(
        "/api/v1/recipes/{}".format(recipe_id), json=json, headers=auth_headers
    )


def get_recipe(client, recipe_id, auth_headers):
    return client.get("/api/v1/recipes/{}".format(recipe_id), headers=auth_headers)


def get_all_recipes(client, auth_headers, page=1, per_page=10, order_by="", desc=False):
    return client.get(
        "/api/v1/recipes?page={}&per_page={}&order_by={}&desc={}".format(
            page, per_page, order_by, desc
        ),
        headers=auth_headers,
    )


def test_not_authorized(client: FlaskClient):
    response = get_all_recipes(client, {})

    assert response.status_code == 401


def test_create_with_supplied_id(client: FlaskClient, auth_headers):
    response = create_recipe(
        client, {"name": "Menu", "_id": "5e4ae04561fe8235a5a18824"}, auth_headers
    )

    assert response.status_code == 201

    response = patch_recipe(
        client,
        "5e4ae04561fe8235a5a18824",
        {"name": "Menu", "_id": "1fe8235a5a5e4ae045618824"},
        auth_headers,
    )

    assert (
        response.status_code == 200
        and response.json["_id"] == "5e4ae04561fe8235a5a18824"
    )

    response = put_recipe(
        client,
        "5e4ae04561fe8235a5a18824",
        {"name": "Menu", "_id": "1fe8235a5a5e4ae045618824"},
        auth_headers,
    )

    assert (
        response.status_code == 200
        and response.json["_id"] == "5e4ae04561fe8235a5a18824"
    )


# def test_create_with_supplied_id_using_put(client: FlaskClient, auth_headers):
#     response = put_recipe(client, '5e4ae04561fe8235a5a18824', {
#         'name': 'Menu',
#         '_id': '5e4ae04561fe8235a5a18824'
#     }, auth_headers)

#     assert response.status_code == 201

#     response = patch_recipe(client, '5e4ae04561fe8235a5a18824', {
#         'name': 'Menu',
#         '_id': '1fe8235a5a5e4ae045618824'
#     }, auth_headers)

#     assert response.status_code == 200 \
#         and response.json['_id'] == '5e4ae04561fe8235a5a18824'

#     response = put_recipe(client, '5e4ae04561fe8235a5a18824', {
#         'name': 'Menu',
#         '_id': '1fe8235a5a5e4ae045618824'
#     }, auth_headers)

#     assert response.status_code == 200 \
#         and response.json['_id'] == '5e4ae04561fe8235a5a18824'

# def test_create_with_different_owner_not_allowed(client: FlaskClient, auth_headers):

#     response = create_recipe(client, {
#         'name': 'ham',
#         'owner': 'pippo'
#     }, auth_headers)

#     assert response.status_code == 403


def test_owner_update(client: FlaskClient, auth_headers):
    response = create_ingredient(client, {"name": "ham"}, auth_headers)

    recipe_id = response.json["_id"]

    # Try to update owner using an integer instead of a string
    response = patch_recipe(client, response.json["_id"], {"owner": 1}, auth_headers)

    assert response.status_code == 400

    # Try to update owner using a valid objectId (from recipe_id)
    response = patch_recipe(client, recipe_id, {"owner": recipe_id}, auth_headers)

    assert response.status_code == 403


def test_duplicate_entry_recipe(client: FlaskClient, auth_headers):
    idx = ObjectId()
    response = create_recipe(
        client, {"_id": idx, "name": "Recipe 1", "ingredients": []}, auth_headers
    )

    assert (
        response.status_code == 201
        and ObjectId(response.json["_id"]) == idx
        and response.json["name"] == "Recipe 1"
    )

    response = create_recipe(
        client, {"_id": idx, "name": "Recipe 2", "ingredients": []}, auth_headers
    )

    assert response.status_code == 409 and response.json["error"] == "DUPLICATE_ENTRY"


def test_create_recipe(client: FlaskClient, auth_headers):
    response = get_all_recipes(client, auth_headers)

    assert (
        response.status_code == 200
        and len(response.json["results"]) == 0
        and response.json["pages"] == 0
    )

    tuna_resp = create_ingredient(client, {"name": "Tuna"}, auth_headers)

    tomato_resp = create_ingredient(client, {"name": "Tomatoes"}, auth_headers)

    response = create_recipe(
        client,
        {
            "name": "Tuna and tomatoes",
            "ingredients": [
                {"ingredient": tuna_resp.json["_id"], "name": "tuna"},
                {"ingredient": tomato_resp.json["_id"], "name": "tomato"},
            ],
            "preparationSteps": [{"description": "Step #1"}],
        },
        auth_headers,
    )

    assert (
        response.status_code == 201
        and response.json["name"] == "Tuna and tomatoes"
        and len(response.json["preparationSteps"]) == 1
    )

    response = get_recipe(client, response.json["_id"], auth_headers)

    assert (
        response.json["name"] == "Tuna and tomatoes"
        and len(response.json["preparationSteps"]) == 1
    )

    # Test fail duplicating ingredient
    # response = create_recipe(client, {
    #  'name': 'Tuna and tomatoes'
    # } , auth_headers)

    # assert response.status_code == 409

    response = create_recipe(client, {"name": "Pizza"}, auth_headers)

    assert response.status_code == 201 and response.json["name"] == "Pizza"

    # Check pagination
    response = get_all_recipes(client, auth_headers, 1, 1)

    assert response.status_code == 200 and response.json["pages"] == 2


def test_replace_recipe(client: FlaskClient, auth_headers):
    response = create_recipe(
        client, {"name": "Tuna and tomatoes", "servs": 2}, auth_headers
    )

    assert response.status_code == 201 and response.json["servs"] == 2

    response = replace_recipe(
        client,
        response.json["_id"],
        {"name": "Tuna and tomatoes", "servs": 3},
        auth_headers,
    )

    assert response.status_code == 200 and response.json["servs"] == 3


def test_duplicate_recipe_allowed(client: FlaskClient, auth_headers):
    response = create_recipe(
        client, {"name": "Tuna and tomatoes", "servs": 2}, auth_headers
    )

    assert response.status_code == 201

    response = create_recipe(
        client, {"name": "Tuna and tomatoes", "servs": 3}, auth_headers
    )

    assert response.status_code == 201

    response = get_all_recipes(client, auth_headers)

    assert (
        response.status_code == 200
        and len(response.json["results"]) == 2
        and response.json["pages"] == 1
    )


def test_update_recipe(client: FlaskClient, auth_headers):
    response = create_recipe(client, {"name": "Tuna and tomatoes"}, auth_headers)

    assert response.status_code == 201 and "description" not in response.json

    response = patch_recipe(
        client,
        response.json["_id"],
        {"name": "Tuna and tomatoes", "description": "Test description"},
        auth_headers,
    )

    assert (
        response.status_code == 200
        and response.json["description"] == "Test description"
    )


@pytest.mark.skip(reason="it gives random errors, needs more checks")
def test_offline_id(client: FlaskClient, auth_headers):
    response = create_recipe(
        client,
        {"_id": "Mf5cd7d4f8cb6cd5acaec6f", "name": "Fish"},  # invalid ObjectId
        auth_headers,
    )

    assert response.status_code == 400

    response = create_recipe(
        client, {"_id": "5f5cd7d4f8cb6cd5acaec6f5", "name": "Fish"}, auth_headers
    )

    assert (
        response.status_code == 201
        and response.json["_id"] == "5f5cd7d4f8cb6cd5acaec6f5"
    )

    idx = response.json["_id"]

    response = put_recipe(
        client,
        idx,
        {"_id": "5f5cd7d4f8cb6cd5acaec6f8", "name": "Fish"},  # Different ObjectId
        auth_headers,
    )

    assert response.status_code == 200 and response.json["_id"] == idx

    response = patch_recipe(
        client,
        idx,
        {"_id": "5f5cd7d4f8cb6cd5acaec6f8", "name": "Fish"},  # Different ObjectId
        auth_headers,
    )

    assert response.status_code == 200 and response.json["_id"] == idx

    response = get_recipe(client, idx, auth_headers)

    assert response.status_code == 200 and response.json["_id"] == idx


def test_create_update_timestamp(client: FlaskClient, auth_headers):
    response = create_recipe(
        client,
        {"name": "Rice", "insert_timestamp": int(datetime.now().timestamp())},
        auth_headers,
    )

    assert (
        response.status_code == 403
        and response.json["error"] == "CANNOT_SET_CREATION_UPDATE_TIME"
    )

    response = create_recipe(
        client,
        {"name": "Rice", "update_timestamp": int(datetime.now().timestamp())},
        auth_headers,
    )

    assert (
        response.status_code == 403
        and response.json["error"] == "CANNOT_SET_CREATION_UPDATE_TIME"
    )

    response = create_recipe(
        client,
        {
            "name": "Rice",
            "update_timestamp": int(datetime.now().timestamp()),
            "insert_timestamp": int(datetime.now().timestamp()),
        },
        auth_headers,
    )

    assert (
        response.status_code == 403
        and response.json["error"] == "CANNOT_SET_CREATION_UPDATE_TIME"
    )

    response = create_recipe(
        client,
        {
            "name": "Rice",
        },
        auth_headers,
    )

    assert (
        response.status_code == 201
        and response.json["insert_timestamp"] is not None
        and isinstance(response.json["insert_timestamp"], int)
        and response.json["update_timestamp"] is not None
        and isinstance(response.json["update_timestamp"], int)
    )

    idx = response.json["_id"]
    insert_timestamp = response.json["insert_timestamp"]
    update_timestamp = response.json["update_timestamp"]

    response = put_recipe(
        client,
        idx,
        {"name": "Tomato", "update_timestamp": int(datetime.now().timestamp())},
        auth_headers,
    )

    assert (
        response.status_code == 403
        and response.json["error"] == "CANNOT_SET_CREATION_UPDATE_TIME"
    )

    response = patch_recipe(
        client,
        idx,
        {"name": "Tomato", "insert_timestamp": int(datetime.now().timestamp())},
        auth_headers,
    )

    assert (
        response.status_code == 403
        and response.json["error"] == "CANNOT_SET_CREATION_UPDATE_TIME"
    )

    response = patch_recipe(
        client,
        idx,
        {
            "name": "Tomato",
            "insert_timestamp": int(datetime.now().timestamp()),
            "update_timestamp": int(datetime.now().timestamp()),
        },
        auth_headers,
    )

    assert (
        response.status_code == 403
        and response.json["error"] == "CANNOT_SET_CREATION_UPDATE_TIME"
    )

    response = put_recipe(
        client,
        idx,
        {
            "name": "Tomato",
            "insert_timestamp": int(datetime.now().timestamp()),
            "update_timestamp": int(datetime.now().timestamp()),
        },
        auth_headers,
    )

    assert (
        response.status_code == 403
        and response.json["error"] == "CANNOT_SET_CREATION_UPDATE_TIME"
    )

    response = patch_recipe(
        client,
        idx,
        {
            "name": "Tomato",
        },
        auth_headers,
    )

    assert (
        response.status_code == 200
        and response.json["insert_timestamp"] == insert_timestamp
        and response.json["update_timestamp"] > update_timestamp
    )

    update_timestamp = response.json["update_timestamp"]

    response = put_recipe(
        client,
        idx,
        {
            "name": "Tomato",
        },
        auth_headers,
    )

    assert (
        response.status_code == 200
        and response.json["name"] == "Tomato"
        and response.json["insert_timestamp"] == insert_timestamp
        and response.json["update_timestamp"] > update_timestamp
    )


def test_get_last_updated(client: FlaskClient, auth_headers):
    response = create_recipe(
        client,
        {
            "name": "Rice",
        },
        auth_headers,
    )

    assert response.status_code == 201

    idx_1 = response.json["_id"]
    insert_timestamp_1 = response.json["insert_timestamp"]
    update_timestamp_1 = response.json["update_timestamp"]

    sleep(1)  # avoid conflicting timestamps

    response = create_recipe(
        client,
        {
            "name": "Tomato",
        },
        auth_headers,
    )

    assert response.status_code == 201

    idx_2 = response.json["_id"]
    insert_timestamp_2 = response.json["insert_timestamp"]
    update_timestamp_2 = response.json["update_timestamp"]

    response = get_all_recipes(
        client, auth_headers, order_by="update_timestamp", desc=True, page=1, per_page=1
    )

    assert (
        response.status_code == 200
        and len(response.json["results"]) == 1
        and response.json["results"][0]["_id"] == idx_2
    )

    response = patch_recipe(
        client,
        idx_1,
        {
            "name": "Rice",
        },
        auth_headers,
    )

    assert (
        response.status_code == 200
        and response.json["insert_timestamp"] == insert_timestamp_1
        and response.json["update_timestamp"] > update_timestamp_1
    )

    update_timestamp_1 = response.json["update_timestamp"]

    response = get_all_recipes(
        client, auth_headers, order_by="update_timestamp", desc=True, page=1, per_page=1
    )

    assert (
        response.status_code == 200
        and len(response.json["results"]) == 1
        and response.json["results"][0]["_id"] == idx_1
        and response.json["results"][0]["update_timestamp"] == update_timestamp_1
    )

    response = put_recipe(
        client,
        idx_1,
        {
            "name": "Rice",
        },
        auth_headers,
    )

    assert (
        response.status_code == 200
        and response.json["insert_timestamp"] == insert_timestamp_1
        and response.json["update_timestamp"] > update_timestamp_1
    )

    update_timestamp_1 = response.json["update_timestamp"]

    response = get_all_recipes(
        client, auth_headers, order_by="update_timestamp", desc=True, page=1, per_page=1
    )

    assert (
        response.status_code == 200
        and len(response.json["results"]) == 1
        and response.json["results"][0]["_id"] == idx_1
        and response.json["results"][0]["update_timestamp"] == update_timestamp_1
    )

    response = patch_recipe(
        client,
        idx_2,
        {
            "name": "Tomato",
        },
        auth_headers,
    )

    assert (
        response.status_code == 200
        and response.json["insert_timestamp"] == insert_timestamp_2
        and response.json["update_timestamp"] > update_timestamp_2
    )

    update_timestamp_2 = response.json["update_timestamp"]

    response = get_all_recipes(
        client, auth_headers, order_by="update_timestamp", desc=True, page=1, per_page=1
    )

    assert (
        response.status_code == 200
        and len(response.json["results"]) == 1
        and response.json["results"][0]["_id"] == idx_2
        and response.json["results"][0]["update_timestamp"] == update_timestamp_2
    )

    response = put_recipe(
        client,
        idx_2,
        {
            "name": "Tomato",
        },
        auth_headers,
    )

    assert (
        response.status_code == 200
        and response.json["insert_timestamp"] == insert_timestamp_2
        and response.json["update_timestamp"] > update_timestamp_2
    )

    update_timestamp_2 = response.json["update_timestamp"]

    response = get_all_recipes(
        client, auth_headers, order_by="update_timestamp", desc=True, page=1, per_page=1
    )

    assert (
        response.status_code == 200
        and len(response.json["results"]) == 1
        and response.json["results"][0]["_id"] == idx_2
        and response.json["results"][0]["update_timestamp"] == update_timestamp_2
    )


def test_allow_unexpected_value(client: FlaskClient, auth_headers):
    ingredient = create_ingredient(client, {"name": "Mozzarella"}, auth_headers)

    response = create_recipe(
        client,
        {
            "name": "Lasagna",
            "unexpected": "field",
            "ingredients": [
                {
                    "ingredient": ingredient.json["_id"],
                    "name": "Mozzarella",
                    "unexpected": "field",
                }
            ],
        },
        auth_headers,
    )

    assert (
        response.status_code == 201
        and "name" in response.json
        and "ingredient" in response.json["ingredients"][0]
        and "unexpected" not in response.json
        and "unexpected" not in response.json["ingredients"][0]
    )

    response = get_recipe(client, response.json["_id"], auth_headers)

    assert (
        response.status_code == 200
        and "name" in response.json
        and "ingredient" in response.json["ingredients"][0]
        and "unexpected" not in response.json
        and "unexpected" not in response.json["ingredients"][0]
    )


def test_related_recipes(client: FlaskClient, auth_headers):
    response = create_recipe(client, {"name": "Tomato sauce"}, auth_headers)

    relatedRecipeId = response.json["_id"]

    response = create_recipe(
        client,
        {"name": "Lasagna", "relatedRecipes": [{"id": relatedRecipeId}]},
        auth_headers,
    )

    assert (
        response.status_code == 201
        and response.json["relatedRecipes"][0]["id"] == relatedRecipeId
    )

    response = get_recipe(client, response.json["_id"], auth_headers)

    assert (
        response.status_code == 200
        and response.json["relatedRecipes"][0]["id"] == relatedRecipeId
    )


def test_unexpected_field_in_recipe_collection(client: FlaskClient, auth_headers):
    tuna = create_ingredient(client, {"name": "tuna"}, auth_headers).json

    response = create_recipe(
        client,
        {
            "name": "Recipe",
            "ingredients": [{"ingredient": tuna["_id"], "name": tuna["name"]}],
        },
        auth_headers,
    )

    assert response.status_code == 201

    saved = Recipe(
        name="Test",
        owner=ObjectId(),
        ingredients=[
            {
                "ingredient": ObjectId(tuna["_id"]),
                "name": "test ingredient",
                "unexpected": 1,
            }
        ],
    ).save()

    assert saved is not None


def test_get_existing_recipe(client: FlaskClient, auth_headers):
    user_profile = get_user_profile(client, auth_headers).json

    db = get_db()
    collection = db.recipes

    doc = collection.insert_one(
        {"name": "Recipe 1", "owner": ObjectId(user_profile["_id"])}
    )

    assert collection.find_one() != None

    recipe = get_recipe(client, doc.inserted_id, auth_headers)

    assert recipe.status_code == 200 and recipe.json["name"] == "Recipe 1"

    recipes = get_all_recipes(client, auth_headers).json

    assert len(recipes["results"]) == 1


def test_create_with_language(client: FlaskClient, auth_headers):
    response = create_recipe(client, {"name": "Menu", "language": "it"}, auth_headers)

    assert response.status_code == 201

    response = get_recipe(
        client,
        response.json["_id"],
        auth_headers,
    )

    assert response.status_code == 200 and response.json["language"] == "it"
