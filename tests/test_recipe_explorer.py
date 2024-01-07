import json


from flask.testing import FlaskClient

from weekly_menu.webapp.api.models import ExternalRecipe

from weekly_menu.lib.recipe_parser import RecipeParserV0


def test_explore_api(client: FlaskClient, auth_headers):
    external_recipes = [
        {"name": "Soup", "scraped": True},
        {"name": "Beans", "scraped": True},
    ]

    for er in external_recipes:
        e = ExternalRecipe.from_json(json.dumps(er))
        e.save()

    len(ExternalRecipe.objects) == 2

    response = client.get(
        "/api/v1/recipes/explore",
        headers=auth_headers,
    )

    assert response.status_code == 200 and len(response.json["results"]) == 2

    response = client.get(
        "/api/v1/recipes/explore?per_page=1",
        headers=auth_headers,
    )

    assert response.status_code == 200 and len(response.json["results"]) == 1
