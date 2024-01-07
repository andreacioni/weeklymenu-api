from flask.testing import FlaskClient

from weekly_menu.lib.recipe_parser import RecipeParserV0


def test_recipe_parser_v0():
    parser = RecipeParserV0()

    json = {"title": "Recipe", "ingredients": []}
    recipe = parser.from_json(json)

    assert recipe.name == json["title"]
    assert len(recipe.ingredients) == 0

    json = {"title": "Recipe 2", "ingredients": ["bread", "milk 200ml"]}
    recipe = parser.from_json(json)

    assert recipe.name == json["title"]
    assert len(recipe.ingredients) == 2

    assert recipe.ingredients[0].name == "bread"
    assert recipe.ingredients[1].name == "milk 200ml"


def test_scrape_api(client: FlaskClient, auth_headers):
    response = client.get(
        "/api/v1/scrapers/recipe?url={}".format(
            "https://ricette.giallozafferano.it/Spaghetti-alla-Norma.html"
        ),
        headers=auth_headers,
    )

    assert (
        response.status_code == 200
        and response.json["name"] == "Pasta alla Norma"
        and response.json["ingredient_parser_version"] == 0
        and "_id" not in response.json
    )
