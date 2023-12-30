import logging
import json

from uuid import uuid4
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from .schema import ImageSchema 
from .. import BASE_PATH
from ...exceptions import ServiceUnavailable

_logger = logging.getLogger(__name__)

_mock = json.loads("""


    {
        "search_metadata":
        {
            "id": "658f4f1ac56d935f38970ab7",
            "status": "Success",
            "json_endpoint": "https://serpapi.com/searches/9262cc60b3da04c3/658f4f1ac56d935f38970ab7.json",
            "created_at": "2023-12-29 22:58:34 UTC",
            "processed_at": "2023-12-29 22:58:34 UTC",
            "google_images_url": "https://www.google.it/search?q=Kebab+vegetariano&oq=Kebab+vegetariano&uule=w+CAIQICIrTWV0cm9wb2xpdGFuIENpdHkgb2YgRmxvcmVuY2UsVHVzY2FueSxJdGFseQ&hl=it&gl=it&tbm=isch",
            "raw_html_file": "https://serpapi.com/searches/9262cc60b3da04c3/658f4f1ac56d935f38970ab7.html",
            "total_time_taken": 0.78
        }
        ,
        "search_parameters":
        {
            "engine": "google_images",
            "q": "Kebab vegetariano",
            "location_requested": "Metropolitan City of Florence, Tuscany, Italy",
            "location_used": "Metropolitan City of Florence,Tuscany,Italy",
            "google_domain": "google.it",
            "hl": "it",
            "gl": "it",
            "device": "desktop"
        }
        ,
        "search_information":
        {
            "image_results_state": "Results for exact spelling",
            "menu_items":
            [
                {
                    "position": 1,
                    "title": "Tutti",
                    "link": "https://www.google.it/search?q=Kebab+vegetariano&source=lmns&gl=it&hl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ0pQJKAB6BAgBEAI",
                    "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google&gl=it&google_domain=google.com&hl=it&q=Kebab+vegetariano"
                }
                ,
                {
                    "position": 2,
                    "title": "Immagini"
                }
                ,
                {
                    "position": 3,
                    "title": "Maps",
                    "link": "https://maps.google.it/maps?q=Kebab+vegetariano&source=lmns&entry=mc&gl=it&hl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQi6AMKAJ6BAgBEAY"
                }
                ,
                {
                    "position": 4,
                    "title": "Video",
                    "link": "https://www.google.it/search?q=Kebab+vegetariano&source=lmns&tbm=vid&gl=it&hl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ0pQJKAN6BAgBEAg",
                    "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_videos&gl=it&google_domain=google.com&hl=it&q=Kebab+vegetariano"
                }
                ,
                {
                    "position": 5,
                    "title": "Libri",
                    "link": "https://www.google.it/search?q=Kebab+vegetariano&source=lmns&tbm=bks&gl=it&hl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ0pQJKAR6BAgBEAo"
                }
                ,
                {
                    "position": 6,
                    "title": "Notizie",
                    "link": "https://www.google.it/search?q=Kebab+vegetariano&source=lmns&tbm=nws&gl=it&hl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ0pQJKAB6BAgBEA0",
                    "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google&gl=it&google_domain=google.com&hl=it&q=Kebab+vegetariano&tbm=nws"
                }
                ,
                {
                    "position": 7,
                    "title": "Voli",
                    "link": "https://www.google.it/travel/flights?q=Kebab+vegetariano&source=lmns&tbm=flm&gl=it&hl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ0pQJKAF6BAgBEA4"
                }
                ,
                {
                    "position": 8,
                    "title": "Finanza",
                    "link": "https://www.google.it/search?q=Kebab+vegetariano&source=lmns&tbm=fin&gl=it&hl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ0pQJKAJ6BAgBEA8"
                }
            ]
        }
        ,
        "suggested_searches":
        [
            {
                "name": "falafel",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:falafel:kaVTgdBz4JU%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoAHoECAEQMQ",
                "chips": "q:kebab+vegetariano,online_chips:falafel:kaVTgdBz4JU%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Afalafel%3AkaVTgdBz4JU%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46ca641665a861dc277cf045ddd60923a2ce.jpeg"
            }
            ,
            {
                "name": "freepik",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:freepik:b8bMCC0VFEQ%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoAXoECAEQMw",
                "chips": "q:kebab+vegetariano,online_chips:freepik:b8bMCC0VFEQ%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Afreepik%3Ab8bMCC0VFEQ%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46caa8bf956c9fc03a75c127bb223d0dd07d.jpeg"
            }
            ,
            {
                "name": "doner kebab",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:doner+kebab:o5_BkEFHIKI%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoAnoECAEQNQ",
                "chips": "q:kebab+vegetariano,online_chips:doner+kebab:o5_BkEFHIKI%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Adoner%2Bkebab%3Ao5_BkEFHIKI%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46cab67cb94a21da02cd8b0afef9494ed174.jpeg"
            }
            ,
            {
                "name": "aioli",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:aioli:vTTROgI5Xc8%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoA3oECAEQNw",
                "chips": "q:kebab+vegetariano,online_chips:aioli:vTTROgI5Xc8%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Aaioli%3AvTTROgI5Xc8%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46cab556751b45c83fa684e158cab8dfb174.jpeg"
            }
            ,
            {
                "name": "pane pita",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:pane+pita:7aIdkpeCcKs%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoBHoECAEQOQ",
                "chips": "q:kebab+vegetariano,online_chips:pane+pita:7aIdkpeCcKs%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Apane%2Bpita%3A7aIdkpeCcKs%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46ca6f77c0a793e26b22efb5db979007a63a.jpeg"
            }
            ,
            {
                "name": "ricetta kebab vegano",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:ricetta+kebab+vegano:mQgCV1ewJEo%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoBXoECAEQOw",
                "chips": "q:kebab+vegetariano,online_chips:ricetta+kebab+vegano:mQgCV1ewJEo%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Aricetta%2Bkebab%2Bvegano%3AmQgCV1ewJEo%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46ca27ee34bb5233ad55ba3aa7dc78fd5d05.jpeg"
            }
            ,
            {
                "name": "burrito",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:burrito:Y11bk7QluXI%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoBnoECAEQPQ",
                "chips": "q:kebab+vegetariano,online_chips:burrito:Y11bk7QluXI%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Aburrito%3AY11bk7QluXI%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46ca4e3de5700108be587aef5204e4cadde1.jpeg"
            }
            ,
            {
                "name": "panino kebab",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:panino+kebab:Keu9X3nd5tE%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoB3oECAEQPw",
                "chips": "q:kebab+vegetariano,online_chips:panino+kebab:Keu9X3nd5tE%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Apanino%2Bkebab%3AKeu9X3nd5tE%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46cae8b8c49725b4255a8b0a5bf1177943f7.jpeg"
            }
            ,
            {
                "name": "salsa",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:salsa:V3Bt3hDtWBY%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoCHoECAEQQQ",
                "chips": "q:kebab+vegetariano,online_chips:salsa:V3Bt3hDtWBY%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Asalsa%3AV3Bt3hDtWBY%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46ca881fc4158b1109daa8d7300fba0dafb9.jpeg"
            }
            ,
            {
                "name": "ricette vegane",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:ricette+vegane:2tB_4UorVI8%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoCXoECAEQQw",
                "chips": "q:kebab+vegetariano,online_chips:ricette+vegane:2tB_4UorVI8%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Aricette%2Bvegane%3A2tB_4UorVI8%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46ca482bdee97f6744e1d0d59383f3d0996d.jpeg"
            }
            ,
            {
                "name": "cucina vegetariana",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:cucina+vegetariana:SQHJCHojaZE%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoCnoECAEQRQ",
                "chips": "q:kebab+vegetariano,online_chips:cucina+vegetariana:SQHJCHojaZE%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Acucina%2Bvegetariana%3ASQHJCHojaZE%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46ca0370958a3b8ae7a2caf05dd5b87ee38a.jpeg"
            }
            ,
            {
                "name": "vegan kebab",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:vegan+kebab:9yw1wN465Hk%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoC3oECAEQRw",
                "chips": "q:kebab+vegetariano,online_chips:vegan+kebab:9yw1wN465Hk%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Avegan%2Bkebab%3A9yw1wN465Hk%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/22ae213decc7e3d53e223c5d005c46ca2dee9f1cbf9ca55ba32098ecc4fa435a.jpeg"
            }
            ,
            {
                "name": "ricetta vegetariana",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:ricetta+vegetariana:htZDl2IAp-Q%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoDHoECAEQSQ",
                "chips": "q:kebab+vegetariano,online_chips:ricetta+vegetariana:htZDl2IAp-Q%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Aricetta%2Bvegetariana%3AhtZDl2IAp-Q%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTKtZwk8UB8crwnP2TAktkLEQvk9t1hDHIcmACloQMEB0CsxvTV9Q&usqp=CAU"
            }
            ,
            {
                "name": "verdure",
                "link": "https://www.google.it/search?q=Kebab+vegetariano&tbm=isch&hl=it&gl=it&chips=q:kebab+vegetariano,online_chips:verdure:rJPCNxm1IWk%3D&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQ4lYoDXoECAEQSw",
                "chips": "q:kebab+vegetariano,online_chips:verdure:rJPCNxm1IWk%3D",
                "serpapi_link": "https://serpapi.com/search.json?chips=q%3Akebab%2Bvegetariano%2Conline_chips%3Averdure%3ArJPCNxm1IWk%253D&device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano",
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSuo0HhIswzble2c0k_LoQg06iAC3l-Sw2Qhsk_Uf1OXXpDqEq2&usqp=CAU"
            }
        ]
        ,
        "images_results":
        [
            {
                "position": 1,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f19656106180b8d3da5e4b6a25049020d2577b97e5ffa0b84bb.jpeg",
                "related_content_id": "Sm1YYUU2R29jQk1zek1cIixcIlRYYTMzMmVJWEtIQWdN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=Sm1YYUU2R29jQk1zek1cIixcIlRYYTMzMmVJWEtIQWdN",
                "source": "Ricette GialloZafferano",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f19656106180b8d3da58d6b72588edccb4e50eab7ccbccc1670.png",
                "title": "Ricetta Kebab vegetariano - La Ricetta di GialloZafferano",
                "link": "https://ricette.giallozafferano.it/Kebab-vegetariano.html",
                "tag": "Ricetta",
                "original": "https://www.giallozafferano.it/images/195-19577/Kebab-vegetariano_780x520_wm.jpg",
                "original_width": 780,
                "original_height": 520,
                "is_product": false
            }
            ,
            {
                "position": 2,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b14f207845595d410ba0d7aa37be08b8c7.jpeg",
                "related_content_id": "QTRXWWdDbE5IRmV2SE1cIixcImMtQ0xwM2REVU5QZTFN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=QTRXWWdDbE5IRmV2SE1cIixcImMtQ0xwM2REVU5QZTFN",
                "source": "CHE Food Revolution",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1331b4d012d68d17eecbbe2efb0ae3d8c.png",
                "title": "Il Doner Kebab Vegetariano fatto in casa con il tipico pane turco",
                "link": "https://chefoodrevolution.com/il-doner-kebab-vegetariano-fatto-in-casa-con-il-tipico-pane-turco/",
                "tag": "Ricetta",
                "original": "https://chefoodrevolution.com/wp-content/uploads/2021/05/Il-Doner-Kebab-Vegetariano.jpg",
                "original_width": 1024,
                "original_height": 954,
                "is_product": false
            }
            ,
            {
                "position": 3,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198325e447a9e7927aa009624ceb10fb3416cefadc5407cc32.jpeg",
                "related_content_id": "a1dramVnakpBVW02a01cIixcImFLcS0tWHU2eXpsbjBN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=a1dramVnakpBVW02a01cIixcImFLcS0tWHU2eXpsbjBN",
                "source": "DonnaD",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198325e447a9e7927ab1263800ee00200741e5a00d833e467c.png",
                "title": "Kebab vegetariano fatto in casa | DonnaD",
                "link": "https://www.donnad.it/kebab-vegetariano-ingredienti-ricetta",
                "original": "https://www.donnad.it/sites/default/files/styles/r_visual_d/public/201819/kebab-vegetariano.jpg?itok=OzLA_V-F",
                "original_width": 678,
                "original_height": 452,
                "is_product": false
            }
            ,
            {
                "position": 4,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f1994c48a6eb1a1236aa5b273abd42436c0ac2b8a1e5c1900ab.jpeg",
                "related_content_id": "ajFRclN1Rl8wTnFVdU1cIixcIk42SHBEQzBOeHA0MFBN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=ajFRclN1Rl8wTnFVdU1cIixcIk42SHBEQzBOeHA0MFBN",
                "source": "GialloZafferano Blog",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f1994c48a6eb1a1236ab833a5d3e46f8f6ae2e58bf57714c473.png",
                "title": "Veggie Kebab - Il Kebab Vegetariano | Le Ricette di Berry",
                "link": "https://blog.giallozafferano.it/lericettediberry/veggie-kebab-kebab-vegetariano/",
                "original": "http://blog.giallozafferano.it/lericettediberry/wp-content/uploads/2014/12/Kebab-Vegetariano.jpg",
                "original_width": 800,
                "original_height": 600,
                "is_product": false
            }
            ,
            {
                "position": 5,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f19d900dd3b4b3faeb6392b61e6f6fc25587b9bae75c5659f57.jpeg",
                "related_content_id": "U2lTd1YxY0NDSm1rNk1cIixcIjVDZlJPVkNXQzlkdlhN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=U2lTd1YxY0NDSm1rNk1cIixcIjVDZlJPVkNXQzlkdlhN",
                "source": "FoodPal",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f19d900dd3b4b3faeb63706917f657c56dbaa5740b44d181077.png",
                "title": "Kebab vegetariano - ricetta | FoodPal",
                "link": "https://www.foodpal-app.com/it/ricette/generale/kebab-vegetariano",
                "original": "https://www.foodpal-app.com/uploads/images/meals/2665/vegetarischer-doener-5f903713ef2dc-800.webp",
                "original_width": 800,
                "original_height": 400,
                "is_product": false
            }
            ,
            {
                "position": 6,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f191cd8a663083fa34a92e600bb32e96e24730fed8b0f86fa63.jpeg",
                "related_content_id": "RmxqdEVONXRjRmRVY01cIixcInh5Z044V1pnMjQxMk5N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=RmxqdEVONXRjRmRVY01cIixcInh5Z044V1pnMjQxMk5N",
                "source": "Love my Salad",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f191cd8a663083fa34a306127d0371f0637e7752686bf545fc3.png",
                "title": "Kebab vegetariano | Love my Salad",
                "link": "https://www.lovemysalad.com/it/ricette/kebab-vegetariano",
                "tag": "Ricetta",
                "original": "https://www.lovemysalad.com/sites/default/files/styles/home_carousel_item_768/public/kebab_11.jpg?itok=PdwRQQyj",
                "original_width": 768,
                "original_height": 400,
                "is_product": false
            }
            ,
            {
                "position": 7,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f19ef9bae83d43938cbaf1728c47f613539e0bc47d55f6df3eb.jpeg",
                "related_content_id": "TUlrYlJjYU92aVJTWk1cIixcInZhWVlDVjZQcVV4VGJN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=TUlrYlJjYU92aVJTWk1cIixcInZhWVlDVjZQcVV4VGJN",
                "source": "Facebook",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f19ef9bae83d43938cb931840920645d97736a32ff39f012040.png",
                "title": "Oriental Fonzie - 🌱 Kebab Vegetariano 🌱 Laffa con Falafel homemade, hummus, Israeli salad, insalata, verza, harissa. Solo da #OrientalFonzie anche Delivery con @justeat_it e @deliveroo_italy | Facebook",
                "link": "https://m.facebook.com/OrientalFonzie/photos/a.2463765210524355/2597146217186253/?type=3&comment_id=2597481573819384&locale=it_IT",
                "original": "https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=2597146217186253",
                "original_width": 990,
                "original_height": 990,
                "is_product": false
            }
            ,
            {
                "position": 8,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f19711320f329b4da3bed6047d01785fae5de48527b43081582.jpeg",
                "related_content_id": "dWg4eDcyVms2MndFLU1cIixcInBlZGthRnpXdmhnaVFN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=dWg4eDcyVms2MndFLU1cIixcInBlZGthRnpXdmhnaVFN",
                "source": "Giulia Nekorkina",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f19711320f329b4da3bf594445b74285be38df82e180107071e.jpeg",
                "title": "Kebab vegetariano - Giulia Nekorkina - Rossa di Sera",
                "link": "https://giulianekorkina.com/2014/08/01/kebab-vegetariano/",
                "original": "https://giulianekorkina.com/wp-content/uploads/2020/06/DSC_0828.jpg",
                "original_width": 1494,
                "original_height": 1000,
                "is_product": false
            }
            ,
            {
                "position": 9,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f19766454108133da941ae40a9564d7c219be35a3d4dd76585d.jpeg",
                "related_content_id": "Zlp5ekhsQXB4TlpiZk1cIixcIkdxRzRFcU9mazJTVFNN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=Zlp5ekhsQXB4TlpiZk1cIixcIkdxRzRFcU9mazJTVFNN",
                "source": "Pinterest",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f19766454108133da94e522c54e3b08f674c9457143e6624e3f.png",
                "title": "Kebab vegetariano | Ricetta | Cibo vegetariano, Ricette, Idee alimentari",
                "link": "https://www.pinterest.it/pin/111604897001831520/",
                "tag": "Ricetta",
                "original": "https://i.pinimg.com/originals/1b/0a/c5/1b0ac5ecf289d13886c1dd480a00ad3a.png",
                "original_width": 600,
                "original_height": 900,
                "is_product": false
            }
            ,
            {
                "position": 10,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198e2a1b89fc4f2082933f3764a02d2a91c95fe0117cfd1188.jpeg",
                "related_content_id": "ZWVRNjNzQTFMUGV1LU1cIixcIllnMVRJQVFJbGk2aUNN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=ZWVRNjNzQTFMUGV1LU1cIixcIllnMVRJQVFJbGk2aUNN",
                "source": "GialloZafferano Blog",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198e2a1b89fc4f2082d1c931af37c0cebcbfb2eb3ba123ccc1.png",
                "title": "Kebab vegetariano | Ricetta di Say Yummy!!!",
                "link": "https://blog.giallozafferano.it/sayummy/kebab-vegetariano-ricetta-etnica/",
                "original": "http://blog.giallozafferano.it/sayummy/wp-content/uploads/2014/03/DSC_2603-1.jpg",
                "original_width": 800,
                "original_height": 616,
                "is_product": false
            }
            ,
            {
                "position": 11,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1d0331f19279aff986406cded1dcd02ca.jpeg",
                "related_content_id": "dktSZ2drMllUMXJmNU1cIixcInBlZGthRnpXdmhnaVFN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=dktSZ2drMllUMXJmNU1cIixcInBlZGthRnpXdmhnaVFN",
                "source": "Giulia Nekorkina",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b140393b29141c50d275255122caf4aea7.jpeg",
                "title": "Kebab vegetariano - Giulia Nekorkina - Rossa di Sera",
                "link": "https://giulianekorkina.com/2014/08/01/kebab-vegetariano/",
                "original": "https://giulianekorkina.com/wp-content/uploads/2020/06/DSC_0844-1024x685.jpg",
                "original_width": 1024,
                "original_height": 685,
                "is_product": false
            }
            ,
            {
                "position": 12,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b15416c3a201d87f77e2e7557b0fdee87c.jpeg",
                "related_content_id": "Rk9qN0pQWDU4RlRyWU1cIixcIm9veUVoMnBSNnRDbmlN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=Rk9qN0pQWDU4RlRyWU1cIixcIm9veUVoMnBSNnRDbmlN",
                "source": "Freepik",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b184f6a8e912dce0ea2ba653f60dc5c87c.png",
                "title": "Kebab vegetariano impacco di verdure pasto fresco cibo spuntino sullo sfondo del cibo dello spazio della copia del tavolo | Foto Premium",
                "link": "https://it.freepik.com/foto-premium/kebab-vegetariano-impacco-di-verdure-pasto-fresco-cibo-spuntino-sullo-sfondo-del-cibo-dello-spazio-della-copia-del-tavolo_36587126.htm",
                "original": "https://img.freepik.com/premium-photo/vegetarian-kebab-wrap-vegetable-fresh-meal-food-snack-table-copy-space-food-background_88242-24439.jpg",
                "original_width": 626,
                "original_height": 417,
                "is_product": false
            }
            ,
            {
                "position": 13,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b13ea2ca52fb10d2cf2746a9d8b2ecffa9.jpeg",
                "related_content_id": "VkRtUlJ1UXo2X2ZMdU1cIixcIlBXN1ZFeHd2bkRscGFN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=VkRtUlJ1UXo2X2ZMdU1cIixcIlBXN1ZFeHd2bkRscGFN",
                "source": "Klausen Express",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1fa83bc04e6858446f9b72de6d70a4177.png",
                "title": "Kebab vegetariano",
                "link": "https://klausenexpress.it/it/product/kebab-vegetariano/",
                "original": "https://klausenexpress.it/wp-content/uploads/2019/02/kebabveg.png",
                "original_width": 500,
                "original_height": 476,
                "is_product": false
            }
            ,
            {
                "position": 14,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1610a984508c72fc6a450d5de7a8fc15e.jpeg",
                "related_content_id": "azNiNW5LWTdtWDVVck1cIixcIkVuMW9tZVE0eFg5YW9N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=azNiNW5LWTdtWDVVck1cIixcIkVuMW9tZVE0eFg5YW9N",
                "source": "Quomi",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1a0c860597b613b26b6e2543624765688.png",
                "title": "Shish kebab vegetariano con insalata e cipolla rossa | Quomi",
                "link": "https://quomi.it/ricetta/shish-kebab-vegetariano-insalata-cipolla-tropea-lime",
                "tag": "Ricetta",
                "original": "https://s3.eu-central-1.amazonaws.com/quomi/media/180365/conversions/Shish-kebab-di-lenticchie-con-insalata-al-lime-thumb-big.jpg",
                "original_width": 1200,
                "original_height": 800,
                "is_product": false
            }
            ,
            {
                "position": 15,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1f210144b3a38e37d10a05539cfd00f7f.jpeg",
                "related_content_id": "YVNHMUdUZkNrNng1Vk1cIixcIjZQSTkzbXJTM3JoZ1JN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=YVNHMUdUZkNrNng1Vk1cIixcIjZQSTkzbXJTM3JoZ1JN",
                "source": "Ortofrutticola ItalVerde",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1c829fa1128908fc29a633717ea115078.png",
                "title": "KEBAB VEGETARIANO - Ortofrutticola ItalVerde",
                "link": "https://ortofrutticolaitalverde.com/2017/02/20/kebab-vegetariano/",
                "original": "https://ortofrutticolaitalverde.com/wp-content/uploads/2017/02/ricetta-kebab-vegetariano.png",
                "original_width": 800,
                "original_height": 450,
                "is_product": false
            }
            ,
            {
                "position": 16,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1f5084a8ca764882f3394159d2d80b902.jpeg",
                "license_details_url": "https://www.alamy.it/licenses-and-pricing/?v=1",
                "related_content_id": "bGVCejBJRlRwWkhEOE1cIixcInBGN3ZQMVBuaTUtU0dN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=bGVCejBJRlRwWkhEOE1cIixcInBGN3ZQMVBuaTUtU0dN",
                "source": "Alamy",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b18e1f75948db1b6d43bfc925aa97df834.png",
                "title": "Falafel con verdure, salsa al pane pita, panino kebab vegetariano. Sfondo nero. Vista dall'alto Foto stock - Alamy",
                "link": "https://www.alamy.it/falafel-con-verdure-salsa-al-pane-pita-panino-kebab-vegetariano-sfondo-nero-vista-dall-alto-image444265734.html",
                "tag": "Su licenza",
                "original": "https://c8.alamy.com/compit/2gpp1da/falafel-con-verdure-salsa-al-pane-pita-panino-kebab-vegetariano-sfondo-nero-vista-dall-alto-2gpp1da.jpg",
                "original_width": 1300,
                "original_height": 954,
                "is_product": false
            }
            ,
            {
                "position": 17,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1c294003cdebfd2ec17761f5aead220ab.jpeg",
                "related_content_id": "QnFNclBLejRIaUdlUk1cIixcIjNKU0VNUFU1bFhFNTdN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=QnFNclBLejRIaUdlUk1cIixcIjNKU0VNUFU1bFhFNTdN",
                "source": "Pinterest",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1cf349054f3569e2e4a36880e2bb03b09.png",
                "title": "Kebab vegetariano | Ricetta | Cibo vegetariano, Idee alimentari, Ricette",
                "link": "https://www.pinterest.it/pin/111604897001572297/",
                "tag": "Ricetta",
                "original": "https://i.pinimg.com/originals/b7/d2/3c/b7d23c206dd521620a6dd7fe2ea8485c.png",
                "original_width": 600,
                "original_height": 900,
                "is_product": false
            }
            ,
            {
                "position": 18,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b15be65ca7b40e2c91745fe4deec0ae47e.jpeg",
                "related_content_id": "bzJueE1OSlVoVmNFV01cIixcIk96YzFsbGdzSnJweE5N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=bzJueE1OSlVoVmNFV01cIixcIk96YzFsbGdzSnJweE5N",
                "source": "Danza de Fogones",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1626cba6289b843bd470652e06b18bf58.png",
                "title": "Kebab Vegano Bajo en Grasa - Danza de Fogones",
                "link": "https://danzadefogones.com/kebab-vegano-bajo-en-grasa/",
                "tag": "Ricetta",
                "original": "https://danzadefogones.com/wp-content/uploads/2016/06/Kebab-vegano-bajo-en-grasa.jpg",
                "original_width": 736,
                "original_height": 1104,
                "is_product": false
            }
            ,
            {
                "position": 19,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b15ca37016edbeb75d43920f24693323f4.jpeg",
                "related_content_id": "QUUxNk81Q3FOVUxlbk1cIixcInF4ZzNUd25GN19WN1pN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=QUUxNk81Q3FOVUxlbk1cIixcInF4ZzNUd25GN19WN1pN",
                "source": "Klausen Express",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b1f558b2497400553d1dacb4eec3fb64d6.png",
                "title": "Dürüm vegetariano in piadina",
                "link": "https://klausenexpress.it/it/product/durum-vegetariano-in-piadina/",
                "original": "https://klausenexpress.it/wp-content/uploads/2019/02/dueruemveg2.png",
                "original_width": 1130,
                "original_height": 1092,
                "is_product": false
            }
            ,
            {
                "position": 20,
                "thumbnail": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b103730ebf85c676d053f6c39934d3b817.jpeg",
                "related_content_id": "YjZjaGVaUElhODIzMk1cIixcIldpU2JlaDFqRzFiR2FN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=YjZjaGVaUElhODIzMk1cIixcIldpU2JlaDFqRzFiR2FN",
                "source": "Facebook",
                "source_logo": "https://serpapi.com/searches/658f4f1ac56d935f38970ab7/images/a20fe54fd0db8f198ed6c351f223c5b169f0da84d6e93fe9b0f438a04e27aacc.png",
                "title": "Kale Kebab - 📢 Que tal iniciar o 2022 mais leve com o nosso KEBAB VEGETARIANO?!😋🌯 . Nele contém👇 ▪️Pão Sírio (tradicional ou integral) tomate seco, rúcula, mix de repolho, alface americana,",
                "link": "https://www.facebook.com/kalekebabrs/photos/a.1349544845205577/2069743823185672/?type=3",
                "original": "https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=2069743823185672",
                "original_width": 1080,
                "original_height": 1080,
                "is_product": false
            }
            ,
            {
                "position": 21,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ6OzC2zAqs8g-0rLJA16GTiWQuutytDKS4KQ&usqp=CAU",
                "related_content_id": "RHJucWVja1BmYlJSZU1cIixcIjJFYmw5c2ZrSzBmUUVN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=RHJucWVja1BmYlJSZU1cIixcIjJFYmw5c2ZrSzBmUUVN",
                "source": "Freepik",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://it.freepik.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab avvolgere verdure fresche pasto vegetariano cibo spuntino sul tavolo copia spazio cibo sfondo | Foto Premium",
                "link": "https://it.freepik.com/foto-premium/kebab-avvolgere-verdure-fresche-pasto-vegetariano-cibo-spuntino-sul-tavolo-copia-spazio-cibo-sfondo_35950823.htm",
                "original": "https://img.freepik.com/premium-photo/kebab-wrap-vegetarian-vegetable-fresh-meal-food-snack-table-copy-space-food-background_88242-24221.jpg",
                "original_width": 626,
                "original_height": 417,
                "is_product": false
            }
            ,
            {
                "position": 22,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQibmLeWyB5bRuXDRghVqm2cADLd8xV7K2Z6w&usqp=CAU",
                "license_details_url": "https://www.istockphoto.com/legal/license-agreement?utm_medium=organic&utm_source=google&utm_campaign=iptcurl",
                "related_content_id": "Ukltd3dNakd3dnZfZE1cIixcIlpwVTJhWUlEejdvY1JN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=Ukltd3dNakd3dnZfZE1cIixcIlpwVTJhWUlEejdvY1JN",
                "source": "iStock",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://istockphoto.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab Vegetariano Stand Gastronomico Nel Mercato Di Brick Lane - Fotografie stock e altre immagini di Ambientazione esterna - iStock",
                "link": "https://www.istockphoto.com/it/foto/kebab-vegetariano-stand-gastronomico-nel-mercato-di-brick-lane-gm1039521112-278276662",
                "tag": "Su licenza",
                "original": "https://media.istockphoto.com/id/1039521112/it/foto/kebab-vegetariano-stand-gastronomico-nel-mercato-di-brick-lane.jpg?s=1024x1024&w=is&k=20&c=qMmnrjty7DUMmrXwrnBfIT0jxJphuClU_UD-AFyGLMU=",
                "original_width": 1024,
                "original_height": 819,
                "is_product": false
            }
            ,
            {
                "position": 23,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJerlIfOtbxNx8BUlLxZ3N5naS4aGg_PQg9A&usqp=CAU",
                "related_content_id": "S2M0UzhCZTlGcXM3S01cIixcInBPczFjVHN1djJZVTBN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=S2M0UzhCZTlGcXM3S01cIixcInBPczFjVHN1djJZVTBN",
                "source": "Ginger & Tomato",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://gingerandtomato.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "kebab - Ginger & Tomato",
                "link": "https://www.gingerandtomato.com/tag/kebab/",
                "original": "https://www.gingerandtomato.com/wp-content/uploads/2015/04/Kebab-allItaliana.jpg",
                "original_width": 600,
                "original_height": 400,
                "is_product": false
            }
            ,
            {
                "position": 24,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSscKSbGHRGs1MPghb0WgXv4eWDYVW2BvX4lw&usqp=CAU",
                "related_content_id": "dzBvcnJFbkgxaWgyQ01cIixcImMzSUN6TTM1SHdtaVRN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=dzBvcnJFbkgxaWgyQ01cIixcImMzSUN6TTM1SHdtaVRN",
                "source": "eBay",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://ebay.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Vegetariano Kebab Vegetariano per Vegani BBQ Uomo S/S Baseball T-Shirt | eBay",
                "link": "https://www.ebay.it/itm/155480237701",
                "original": "https://i.ebayimg.com/images/g/-dcAAOSwfIVj6brj/s-l1200.jpg",
                "original_width": 1200,
                "original_height": 1200,
                "is_product": false
            }
            ,
            {
                "position": 25,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQu5AA-Fs_0XnBbZ8iqqGmHAm9dMVkva0QB9A&usqp=CAU",
                "related_content_id": "c3hoVnBwLU82Rm1RYU1cIixcIlVyeTNuSVljYVNjTEdN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=c3hoVnBwLU82Rm1RYU1cIixcIlVyeTNuSVljYVNjTEdN",
                "source": "La Cucina Italiana",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://lacucinaitaliana.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Mai assaggiato kebab vegetale? | La Cucina Italiana",
                "link": "https://www.lacucinaitaliana.it/gallery/kebab-vegetale-carne-alternativa-planted/",
                "original": "https://media-assets.lacucinaitaliana.it/photos/63d3c7aa4095617103c9b953/master/pass/kebab%20vegetale%20planted%201.jpg",
                "original_width": 1700,
                "original_height": 1080,
                "is_product": false
            }
            ,
            {
                "position": 26,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSAFRF61E-vfHx7ACe6gjRVN_3pp84FlhYNCQ&usqp=CAU",
                "related_content_id": "SVVuU0lqaFNLZTdqMU1cIixcIm9saHRuekNUVy1xbHZN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=SVVuU0lqaFNLZTdqMU1cIixcIm9saHRuekNUVy1xbHZN",
                "source": "Vecteezy",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://it.vecteezy.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "doner kebab vegetale shawarma burrito ripieno pita vegetariano vegetariano 5443352 Stock Photo su Vecteezy",
                "link": "https://it.vecteezy.com/foto/5443352-doner-kebab-vegetable-shawarma-burrito-filling-veggie-pita-vegetariano",
                "original": "https://static.vecteezy.com/ti/foto-gratuito/p2/5443352-doner-kebab-vegetable-shawarma-burrito-filling-veggie-pita-vegetariano-foto.jpg",
                "original_width": 1307,
                "original_height": 1960,
                "is_product": false
            }
            ,
            {
                "position": 27,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRL-DC08IjeLeJ8wtfwOs-u4cGtjbYfpk4Eqg&usqp=CAU",
                "related_content_id": "cG9ZdnZNam4teUs3X01cIixcIk5JbEtXczNfLUxoS2xN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=cG9ZdnZNam4teUs3X01cIixcIk5JbEtXczNfLUxoS2xN",
                "source": "Tripadvisor",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://tripadvisor.com.br&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegetariano – Foto de O Kebab, São Paulo - Tripadvisor",
                "link": "https://www.tripadvisor.com.br/LocationPhotoDirectLink-g303631-d13187198-i334646152-O_Kebab-Sao_Paulo_State_of_Sao_Paulo.html",
                "original": "https://media-cdn.tripadvisor.com/media/photo-i/13/f2/4b/88/kebab-vegetariano.jpg",
                "original_width": 180,
                "original_height": 200,
                "is_product": false
            }
            ,
            {
                "position": 28,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4usXnclgv91zmNaxgRHGK0pQj75dtBondTQ&usqp=CAU",
                "related_content_id": "MUZURjdYc2VuMUwwOU1cIixcIko4QnFrUmJhN2xXMDNN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=MUZURjdYc2VuMUwwOU1cIixcIko4QnFrUmJhN2xXMDNN",
                "source": "Wired Italia",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://wired.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Com'è il kebab vegetale? Noi lo abbiamo assaggiato | Wired Italia",
                "link": "https://www.wired.it/article/kebab-vegetale-planted-assaggio-gianluca-vacchi/",
                "original": "https://media-assets.wired.it/photos/61c20e8dbbb02995179b57d2/16:9/w_2560%2Cc_limit/IMG-6456.jpg",
                "original_width": 2560,
                "original_height": 1440,
                "is_product": false
            }
            ,
            {
                "position": 29,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTUdNLUZERPm9optdD4LxF78BE2xCULBMk6zQ&usqp=CAU",
                "license_details_url": "https://www.alamy.it/licenses-and-pricing/?v=1",
                "related_content_id": "RG82b0kxby1Sd3E2bU1cIixcInRkdk9wdXJBQ1FDWnZN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=RG82b0kxby1Sd3E2bU1cIixcInRkdk9wdXJBQ1FDWnZN",
                "source": "Alamy",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://alamy.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegetariano con pane piatto Shawarma con pistacchi, melanzane/melanzane, formaggio, pomodori e peperone verde. Kebap. Alimenti biologici sani Foto stock - Alamy",
                "link": "https://www.alamy.it/kebab-vegetariano-con-pane-piatto-shawarma-con-pistacchi-melanzane-melanzane-formaggio-pomodori-e-peperone-verde-kebap-alimenti-biologici-sani-image350257502.html",
                "tag": "Su licenza",
                "original": "https://c8.alamy.com/compit/2b9rh0e/kebab-vegetariano-con-pane-piatto-shawarma-con-pistacchi-melanzane-melanzane-formaggio-pomodori-e-peperone-verde-kebap-alimenti-biologici-sani-2b9rh0e.jpg",
                "original_width": 1300,
                "original_height": 956,
                "is_product": false
            }
            ,
            {
                "position": 30,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSsnk1gX5NzbmL2y9EjQZvXDlEBJUDm4aVDyw&usqp=CAU",
                "related_content_id": "ZGR1T09wcGNJcHRDSk1cIixcIkNXbWJVdk9qbVBiNGJN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=ZGR1T09wcGNJcHRDSk1cIixcIkNXbWJVdk9qbVBiNGJN",
                "source": "Casa Abril",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://casa.abril.com.br&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegetariano de berinjela: rápido, prático e saboroso! | CASA.COM.BR",
                "link": "https://casa.abril.com.br/bem-estar/kebab-vegetariano-de-berinjela-rapido-pratico-e-saboroso",
                "original": "https://casa.abril.com.br/wp-content/uploads/2016/12/kebab2.jpeg?quality=70&strip=all",
                "original_width": 550,
                "original_height": 366,
                "is_product": false
            }
            ,
            {
                "position": 31,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSqzmU9aX1unCegta_50r-_1U9eKsFVVCUV8A&usqp=CAU",
                "license_details_url": "https://support.vecteezy.com/en_us/new-vecteezy-licensing-ByHivesvt",
                "related_content_id": "R19FN1plSzZqY1pPNk1cIixcInM0SHJmVFNPWVEwTWZN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=R19FN1plSzZqY1pPNk1cIixcInM0SHJmVFNPWVEwTWZN",
                "source": "Vecteezy",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://it.vecteezy.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "doner kebab vegetale shawarma burrito ripieno pita vegetariano vegetariano 5443316 Stock Photo su Vecteezy",
                "link": "https://it.vecteezy.com/foto/5443316-doner-kebab-vegetable-shawarma-burrito-filling-veggie-pita-vegetariano",
                "tag": "Su licenza",
                "original": "https://static.vecteezy.com/ti/foto-gratuito/p1/5443316-doner-kebab-vegetable-shawarma-burrito-filling-veggie-pita-vegetariano-foto.jpg",
                "original_width": 1470,
                "original_height": 980,
                "is_product": false
            }
            ,
            {
                "position": 32,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLhSW9Gu8pNjviwGGNCYOD2zNXAeIBA-KOYg&usqp=CAU",
                "related_content_id": "c2lTZFFWNjFkaGNHeE1cIixcIm1oLVd3OVpNOXE0dFBN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=c2lTZFFWNjFkaGNHeE1cIixcIm1oLVd3OVpNOXE0dFBN",
                "source": "Tripadvisor",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://tripadvisor.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "VASSOIO DA ASPORTO KEBAB VEGETARIANO - Picture of Romolo's Food & Drink, Sicily - Tripadvisor",
                "link": "https://www.tripadvisor.com/LocationPhotoDirectLink-g187889-d7702817-i125441328-Romolo_s_Food_Drink-Messina_Province_of_Messina_Sicily.html",
                "original": "https://media-cdn.tripadvisor.com/media/photo-s/16/01/71/8e/romolo-s-kebab.jpg",
                "original_width": 550,
                "original_height": 410,
                "is_product": false
            }
            ,
            {
                "position": 33,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkgj2Mz5616CEkKD4LzghJvfTg7Iw14ykf5w&usqp=CAU",
                "related_content_id": "dE1XdE54NTRQbG80ME1cIixcIk9laUNfMHlSWS1XVllN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=dE1XdE54NTRQbG80ME1cIixcIk9laUNfMHlSWS1XVllN",
                "source": "Ricette in Tv",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://ricetteintv.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Cucina con Nigella | Ricetta kebab vegetariano",
                "link": "https://www.ricetteintv.com/cucina-con-nigella-la-ricetta-del-kebab-vegetariano/",
                "original": "https://www.ricetteintv.com/?attachment_id=11832",
                "original_width": 818,
                "original_height": 459,
                "is_product": false
            }
            ,
            {
                "position": 34,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjg48K3gd2D3qj5Bq-3s_ISsn-DZCYTcBBjA&usqp=CAU",
                "related_content_id": "UHdvNDVrLVEwNHFhOU1cIixcIlB4NG80TE9id21wbkRN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=UHdvNDVrLVEwNHFhOU1cIixcIlB4NG80TE9id21wbkRN",
                "source": "unavegetarianaincucina",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://unavegetarianaincucina.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Veggie kebab -",
                "link": "https://unavegetarianaincucina.it/veggie-kebab/",
                "original": "http://unavegetarianaincucina.it/wp-content/uploads/2014/07/IMG_2083-Copia-e1406280581780.jpg",
                "original_width": 600,
                "original_height": 900,
                "is_product": false
            }
            ,
            {
                "position": 35,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQLRLuiCEjUtw5IQ6OdV2JSUfDg9PilOnOuCA&usqp=CAU",
                "license_details_url": "https://it.123rf.com/license_summary.php",
                "related_content_id": "dHBWSVdoTmwtMndYeE1cIixcImhaZzN2amNjT1ZTOWJN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=dHBWSVdoTmwtMndYeE1cIixcImhaZzN2amNjT1ZTOWJN",
                "source": "123RF",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://it.123rf.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Immagini Stock - Potato Kebab Vegetariano, Spiedo Con Verdure, Pomodoro, Erbe Sul Bastone, Gustoso Piatto Picnic. Image 28153022",
                "link": "https://it.123rf.com/photo_28153022_potato-vegetarian-kebab,-skewer-with-vegetables,-tomato,-herb-on-stick,-tasty-picnic-dish.html",
                "tag": "Su licenza",
                "original": "https://previews.123rf.com/images/marialapina/marialapina1405/marialapina140500143/28153022-potato-kebab-vegetariano-spiedo-con-verdure-pomodoro-erbe-sul-bastone-gustoso-piatto-picnic.jpg",
                "original_width": 1300,
                "original_height": 866,
                "is_product": false
            }
            ,
            {
                "position": 36,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR2DZhVbeSSy8gvZd4CI5NI7mpNmLJCz1puYQ&usqp=CAU",
                "license_details_url": "https://it.dreamstime.com/about-stock-image-licenses?id=29926188",
                "related_content_id": "SzJweTRYZDg5UVRhOE1cIixcIkJBYWM5OThxSGZaYkxN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=SzJweTRYZDg5UVRhOE1cIixcIkJBYWM5OThxSGZaYkxN",
                "source": "Dreamstime",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://it.dreamstime.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab di verdure fotografia stock. Immagine di sano, spiedo - 29926188",
                "link": "https://it.dreamstime.com/fotografie-stock-libere-da-diritti-chiuda-su-sul-kebab-vegetariano-dello-spiedo-image29926188",
                "tag": "Su licenza",
                "original": "https://thumbs.dreamstime.com/z/chiuda-su-sul-kebab-vegetariano-dello-spiedo-29926188.jpg",
                "original_width": 1067,
                "original_height": 1690,
                "is_product": false
            }
            ,
            {
                "position": 37,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRAmhAJv3fMe-w8kaBLW_0gsIUMKm6pEd9whw&usqp=CAU",
                "related_content_id": "MTh1UEJsTDlQekkwQU1cIixcIkZNNHRJR2RHZ3lmY2pN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=MTh1UEJsTDlQekkwQU1cIixcIkZNNHRJR2RHZ3lmY2pN",
                "source": "GQ Italia",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://gqitalia.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "1416411008_Kebab-Vegetariano.jpg",
                "link": "https://www.gqitalia.it/fullscreen/?wpID=31924&wpPos=0&oldGalleryID=&openGallery=",
                "original": "https://img.gqitalia.it/wp-content/uploads/2014/11/1416411008_Kebab-Vegetariano.jpg",
                "original_width": 1000,
                "original_height": 666,
                "is_product": false
            }
            ,
            {
                "position": 38,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSe3I37JiBfbpECK0k_27atiooZ2zKzIc3Amg&usqp=CAU",
                "related_content_id": "aGZ4SXZmT0lZYWxlWU1cIixcIkVrQ1dwMnNIbExSNlZN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=aGZ4SXZmT0lZYWxlWU1cIixcIkVrQ1dwMnNIbExSNlZN",
                "source": "SoloFornelli.it",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://solofornelli.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Ricetta: Kebab vegetariano | SoloFornelli.it",
                "link": "https://www.solofornelli.it/ricetta-kebab-vegetariano/",
                "original": "https://www.solofornelli.it/wp-content/uploads/2016/04/Kebab-vegano.gif",
                "original_width": 450,
                "original_height": 267,
                "is_product": false
            }
            ,
            {
                "position": 39,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQf-GqAk2F1sKMhiEVx-tRNX6hfksl_k2KRcg&usqp=CAU",
                "related_content_id": "TnRSWldCSHYwM0NzRU1cIixcIkNfam5aTnkxT0tnSmdN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=TnRSWldCSHYwM0NzRU1cIixcIkNfam5aTnkxT0tnSmdN",
                "source": "cookpad.com",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://cookpad.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegetariano Receta de Kami- Cookpad",
                "link": "https://cookpad.com/es/recetas/7931794-kebab-vegetariano",
                "original": "https://img-global.cpcdn.com/recipes/bf195572577db46a/680x482cq70/kebab-vegetariano-foto-principal.jpg",
                "original_width": 680,
                "original_height": 482,
                "is_product": false
            }
            ,
            {
                "position": 40,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQUZH-4sa01Gdx5aoQiupQmN_BR5d_wMaSKAw&usqp=CAU",
                "related_content_id": "M0k0eTUyLVJmdGYtTE1cIixcIllnMVRJQVFJbGk2aUNN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=M0k0eTUyLVJmdGYtTE1cIixcIllnMVRJQVFJbGk2aUNN",
                "source": "GialloZafferano Blog",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://blog.giallozafferano.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegetariano | Ricetta di Say Yummy!!!",
                "link": "https://blog.giallozafferano.it/sayummy/kebab-vegetariano-ricetta-etnica/",
                "original": "http://blog.giallozafferano.it/sayummy/wp-content/uploads/2014/03/DSC_2602-1.jpg",
                "original_width": 533,
                "original_height": 800,
                "is_product": false
            }
            ,
            {
                "position": 41,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWs6Ncta_opaO4fJ6Xe6Om5m-iJGQZ0qcoaQ&usqp=CAU",
                "related_content_id": "NVNEMXM4RjJnN05UVk1cIixcIkNjWmYwcnhTbjBaMEFN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=NVNEMXM4RjJnN05UVk1cIixcIkNjWmYwcnhTbjBaMEFN",
                "source": "Agrodolce",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://agrodolce.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Come farcire un panino kebab - Agrodolce",
                "link": "https://www.agrodolce.it/2023/06/14/come-farcire-panino-kebab/",
                "original": "https://cdn.agrodolce.it/8pThOsUTXPSduhCyEd-Njt0Y4VQ=/640x427/smart/https://www.agrodolce.it/app/uploads/2023/06/kebab-vegetariano.jpg",
                "original_width": 640,
                "original_height": 427,
                "is_product": false
            }
            ,
            {
                "position": 42,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRiH_zoLfxcARuUc7zyqglD8IiNGdOZ1d7AFQ&usqp=CAU",
                "related_content_id": "Qy11ZmpwX29ITEFXUE1cIixcInl2NHNDb25ZdFB2YTFN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=Qy11ZmpwX29ITEFXUE1cIixcInl2NHNDb25ZdFB2YTFN",
                "source": "Scienze - Fanpage",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://scienze.fanpage.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Cinque bufale sul kebab che dovete smettere di condividere",
                "link": "https://scienze.fanpage.it/cinque-bufale-sul-kebab-che-dovete-smettere-di-condividere/",
                "original": "https://staticfanpage.akamaized.net/wp-content/uploads/sites/5/2017/12/kebab-bufale2.jpg",
                "original_width": 2048,
                "original_height": 1715,
                "is_product": false
            }
            ,
            {
                "position": 43,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSTxqtE4DSFFX0FdhCoQy-2OTar0g0kveYfOg&usqp=CAU",
                "related_content_id": "WHFSS3p4cFNsRzJiVk1cIixcIlpGVkVxT3JpRUFmYkdN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=WHFSS3p4cFNsRzJiVk1cIixcIlpGVkVxT3JpRUFmYkdN",
                "source": "Fysis.it",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://fysis.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab Vegano - Ricetta con Seitan | Fysis.it",
                "link": "https://fysis.it/kebap-vegan/",
                "original": "https://fysis.it/wp-content/uploads/kebab.jpg",
                "original_width": 800,
                "original_height": 532,
                "is_product": false
            }
            ,
            {
                "position": 44,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcROML23Fc1ltzaQ-4TC5CFCTrH4vtJUs92A7A&usqp=CAU",
                "related_content_id": "TTEwZnhjRWkwSEk4eU1cIixcImh2eDlrZWtrVzdSSV9N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=TTEwZnhjRWkwSEk4eU1cIixcImh2eDlrZWtrVzdSSV9N",
                "source": "abillion",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://abillion.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Anatolia - Arabian Kebab Siracusa, Italy Kebab vegetariano Review | abillion",
                "link": "https://www.abillion.com/reviews/621401ae2b88d8009e5f6fe1",
                "original": "https://imagedelivery.net/olI9wp0b6luWFB9nPfnqjQ/res/abillionveg/image/upload/crz24i64xv6hq1grkpp6/1645478251.jpg/w=720",
                "original_width": 720,
                "original_height": 720,
                "is_product": false
            }
            ,
            {
                "position": 45,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQMwuUXM5RUeSOhr9Z_nTt3GC3LBtn9cu4Q5A&usqp=CAU",
                "related_content_id": "aTgwYjhwNWppLVNFdU1cIixcIkw5NDltS01qZE03RXFN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=aTgwYjhwNWppLVNFdU1cIixcIkw5NDltS01qZE03RXFN",
                "source": "Cucina Naturale",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://cucina-naturale.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegan al seitan - Cucina Naturale",
                "link": "https://www.cucina-naturale.it/ricette/kebab-vegan-al-seitan/",
                "tag": "Ricetta",
                "original": "http://www.cucina-naturale.it/wp-content/uploads/2016/11/20162Fmaggio2Fkebabveganalseitan-1.jpg",
                "original_width": 1280,
                "original_height": 1099,
                "is_product": false
            }
            ,
            {
                "position": 46,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSDx84HYu2uYEeo1faHADSMNibrdaqHqzMvlg&usqp=CAU",
                "related_content_id": "OWZ5T0RJR2dDUGp6cU1cIixcIm5PWXV5b1ZNcjBXWkpN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=OWZ5T0RJR2dDUGp6cU1cIixcIm5PWXV5b1ZNcjBXWkpN",
                "source": "Okdiario",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://okdiario.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegano: receta fácil",
                "link": "https://okdiario.com/recetas/receta-kebab-veganos-5567067",
                "tag": "Ricetta",
                "original": "https://okdiario.com/img/2020/05/18/kebab-vega-655x368.jpg",
                "original_width": 655,
                "original_height": 368,
                "is_product": false
            }
            ,
            {
                "position": 47,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRExAbs9a75KjtpjLD6-_xHqgSN-mLoGy3vQQ&usqp=CAU",
                "license_details_url": "http://www.mondadoriphoto.com",
                "related_content_id": "X3g0eXZvazVLZzl2bE1cIixcIlZETHdCOHFmbzhUTWJN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=X3g0eXZvazVLZzl2bE1cIixcIlZETHdCOHFmbzhUTWJN",
                "source": "Sale&Pepe",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://salepepe.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab di seitan e cipolle con maionese vegetale - Sale&Pepe",
                "link": "https://www.salepepe.it/ricette/lieviti/piadine/kebab-di-seitan-e-cipolle-con-maionese-vegetale/",
                "original": "https://www.salepepe.it/files/2023/02/AA606050_alta-1140x636.jpg",
                "original_width": 1140,
                "original_height": 636,
                "is_product": false
            }
            ,
            {
                "position": 48,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4n3VUd18gtpb1fQInR551uPVmoU9leeBOxg&usqp=CAU",
                "related_content_id": "d3gzaG5pR25oVy1IU01cIixcIk9feXl6Vm51cFZKMGpN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=d3gzaG5pR25oVy1IU01cIixcIk9feXl6Vm51cFZKMGpN",
                "source": "ABC Allenamento",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://abcallenamento.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab da Culturista all'Italiana",
                "link": "https://www.abcallenamento.it/blog-alimentazione/ricette/kebab-da-culturista-all-italiana/",
                "original": "https://www.abcallenamento.it/wp-content/uploads/2021/10/kebab-vegetariano.600x420.36964.jpg",
                "original_width": 600,
                "original_height": 358,
                "is_product": false
            }
            ,
            {
                "position": 49,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQMm0G_Q4a6TOgeOy3SDDEFG-0Fw6EUfquqlQ&usqp=CAU",
                "related_content_id": "X2syMVcyWnphZ3RHYk1cIixcIkdsZ0tMQ2VSLUtET1JN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=X2syMVcyWnphZ3RHYk1cIixcIkdsZ0tMQ2VSLUtET1JN",
                "source": "Il Cucchiaio Verde",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://ilcucchiaioverde.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab veg - Il Cucchiaio Verde",
                "link": "https://www.ilcucchiaioverde.com/kebab-veg/",
                "tag": "Ricetta",
                "original": "https://www.ilcucchiaioverde.com/wp-content/uploads/2016/07/Kebab-vegan.jpg",
                "original_width": 1200,
                "original_height": 798,
                "is_product": false
            }
            ,
            {
                "position": 50,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBINjdQCGzvEWnzR4I8DkdgjeTwXEcvzFsfw&usqp=CAU",
                "related_content_id": "UUlvWF9qRGthM1VONU1cIixcIjlmeHRSNjdwT1dRT05N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=UUlvWF9qRGthM1VONU1cIixcIjlmeHRSNjdwT1dRT05N",
                "source": "la Repubblica",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://repubblica.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Nel Ghetto di Roma il kebab d'autore di Oriental Fonzie - la Repubblica",
                "link": "https://www.repubblica.it/sapori/2020/08/24/news/roma_recensione_locale_oriental_fonzie-262179647/",
                "original": "https://www.repstatic.it/content/nazionale/img/2020/08/17/173501194-82c2dc2c-de5c-45ca-a4bb-4833c64c2983.jpg",
                "original_width": 558,
                "original_height": 335,
                "is_product": false
            }
            ,
            {
                "position": 51,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkF1NPmhWwsCrdD-tlTC2e3Mf_boZoSB6GvA&usqp=CAU",
                "related_content_id": "WXVfd0t6c1pKYktOYk1cIixcIll4NUlLQTRPNVdEQldN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=WXVfd0t6c1pKYktOYk1cIixcIll4NUlLQTRPNVdEQldN",
                "source": "Deliveroo",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://deliveroo.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Grifo Kebab consegna in zona Perugia - Ordina su Deliveroo",
                "link": "https://deliveroo.it/it/menu/perugia/perugia/grifo-kebab-perugia",
                "original": "https://rs-menus-api.roocdn.com/images/c15774e7-f268-44c4-a119-fbfe2709c712/image.jpeg",
                "original_width": 1296,
                "original_height": 864,
                "is_product": false
            }
            ,
            {
                "position": 52,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQao1ykuLaV1VABOXzQTfKX6g8Yyux-cq8Wag&usqp=CAU",
                "related_content_id": "VjR2dGlNRXJvTWJhN01cIixcImwwWnJUSkFrUVFFc0xN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=VjR2dGlNRXJvTWJhN01cIixcImwwWnJUSkFrUVFFc0xN",
                "source": "Pasticceria del corso",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://pasticceriadelcorso.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegano - Prodotti per vegani - Kebab verdure",
                "link": "https://www.pasticceriadelcorso.it/vegano/prodotti-per-vegani/kebab-vegano.asp",
                "original": "https://www.pasticceriadelcorso.it/vegano/prodotti-per-vegani/kebab-vegano_NG2.jpg",
                "original_width": 745,
                "original_height": 497,
                "is_product": false
            }
            ,
            {
                "position": 53,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJYyzMkz23Cch10_6rXuiM1Jflk4u344JNoQ&usqp=CAU",
                "related_content_id": "MWQ5Q0FoSnMzNGxiT01cIixcIlBtU1llU1lqZDl2MjVN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=MWQ5Q0FoSnMzNGxiT01cIixcIlBtU1llU1lqZDl2MjVN",
                "source": "MILANOEVENTS.IT",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://milanoevents.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "BABEK: a Milano il kebab è bio e vegetariano in versione turco-siciliana",
                "link": "https://milanoevents.it/2017/04/26/babek-kebab-bio-vegetariano/",
                "original": "https://milanoevents.it/wp-content/uploads/2017/04/BABEK_.jpg",
                "original_width": 2000,
                "original_height": 1333,
                "is_product": false
            }
            ,
            {
                "position": 54,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRtrv9R6ENZVhGq2Ii0CmQYxhqzw_ptgzz29g&usqp=CAU",
                "related_content_id": "VlAwWDBpMTI4XzJjcE1cIixcIkFMcU9DcGhEa3FpRldN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=VlAwWDBpMTI4XzJjcE1cIixcIkFMcU9DcGhEa3FpRldN",
                "source": "Fine Food Group",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://finefoodgroup.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "PLANTED KEBAB | Fine Food Group",
                "link": "https://www.finefoodgroup.com/tool/it/products/vegano-e-vegetariano/veg/planted-kebab/pb09f",
                "original": "https://www.finefoodgroup.com/images/PB09F.jpg",
                "original_width": 500,
                "original_height": 500,
                "is_product": false
            }
            ,
            {
                "position": 55,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxhHMCnvUhsR0vqXHf_x8huKREZSE8yH47Zw&usqp=CAU",
                "related_content_id": "VktmY20zbU1BTzd3WE1cIixcImdtWGRBSXZnSzJ2LTdN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=VktmY20zbU1BTzd3WE1cIixcImdtWGRBSXZnSzJ2LTdN",
                "source": "Easy Cheesy Vegetarian",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://easycheesyvegetarian.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Vegetarian Doner Kebab (with halloumi cheese!) - Easy Cheesy Vegetarian",
                "link": "https://www.easycheesyvegetarian.com/vegetarian-doner-kebab/",
                "original": "https://www.easycheesyvegetarian.com/wp-content/uploads/2020/02/Vegetarian-doner-kebab-11-6-650x975.jpg",
                "original_width": 650,
                "original_height": 975,
                "is_product": false
            }
            ,
            {
                "position": 56,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRShKYmWiqZPb167_F8hefPHeUTxm3I3N3ejA&usqp=CAU",
                "related_content_id": "T0lISVZZQUhOcVZIZE1cIixcImtwZE1WelJNVlhXLS1N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=T0lISVZZQUhOcVZIZE1cIixcImtwZE1WelJNVlhXLS1N",
                "source": "Freepik",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://it.freepik.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegetariano impacco di verdure pasto fresco cibo spuntino sullo sfondo del cibo dello spazio della copia del tavolo | Foto Premium",
                "link": "https://it.freepik.com/foto-premium/kebab-vegetariano-impacco-di-verdure-pasto-fresco-cibo-spuntino-sullo-sfondo-del-cibo-dello-spazio-della-copia-del-tavolo_36587145.htm",
                "original": "https://img.freepik.com/premium-photo/vegetarian-kebab-wrap-vegetable-fresh-meal-food-snack-table-copy-space-food-background_88242-24448.jpg",
                "original_width": 417,
                "original_height": 626,
                "is_product": false
            }
            ,
            {
                "position": 57,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLdm0PZ9J1hFXU98iMUk_x-e1D13PE7aliIA&usqp=CAU",
                "related_content_id": "Q0oxWnRBcmxMdGQwR01cIixcIlZGMzlVdUVBUExCMXZN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=Q0oxWnRBcmxMdGQwR01cIixcIlZGMzlVdUVBUExCMXZN",
                "source": "Sissiland",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://sissiland.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegano: la ricetta che non ha nulla da invidiare a quella tradizionale a base di carne – Sissiland",
                "link": "https://www.sissiland.it/kebab-veg/",
                "original": "https://www.sissiland.it/wp-content/uploads/2021/02/Ricett_kebab_vegano_-senza_carne_Come_fare_-il_-kebab_fatto_in_-casa_in_versione_vegana_ricetta-kebab-vegano-scaled.jpg",
                "original_width": 2560,
                "original_height": 1920,
                "is_product": false
            }
            ,
            {
                "position": 58,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQDz853-wtINqVNXjx1ASZtUr_NitcldehRbw&usqp=CAU",
                "related_content_id": "WlhQbzM2Qm53Rmpza01cIixcIm9hRm13Zi1makctMWtN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=WlhQbzM2Qm53Rmpza01cIixcIm9hRm13Zi1makctMWtN",
                "source": "eBay",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://ebay.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Vegetariano Kebab Vegetariano per Vegani BBQ Bambini Felpa Maglione | eBay",
                "link": "https://www.ebay.it/itm/176054118953",
                "original": "https://i.ebayimg.com/images/g/2SIAAOSwFAFj7orz/s-l1200.jpg",
                "original_width": 1200,
                "original_height": 1200,
                "is_product": false
            }
            ,
            {
                "position": 59,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT0l3Khc0UumCiikFWGPyt-Cl96FT17vplxkQ&usqp=CAU",
                "related_content_id": "MnZOTm1UQV8wWngzeU1cIixcIjRLSXo0Q01jUkJ1MVJN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=MnZOTm1UQV8wWngzeU1cIixcIjRLSXo0Q01jUkJ1MVJN",
                "source": "Hesitant Explorers",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://hesitantexplorers.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Ali Babà Kebab: recensione oltre il mito e la leggenda",
                "link": "https://www.hesitantexplorers.com/recensioni/ali-baba-kebab/",
                "original": "https://www.hesitantexplorers.com/wp-content/uploads/2021/05/Ali-Baba-e1629390920979.webp",
                "original_width": 400,
                "original_height": 533,
                "is_product": false
            }
            ,
            {
                "position": 60,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgH1jRkvvQwTFf0zYkEhZWd0Ig_cADyK-udw&usqp=CAU",
                "related_content_id": "aVpTWkRKclFuN3dVOU1cIixcIlY1RXFIeHpSRDVOdnpN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=aVpTWkRKclFuN3dVOU1cIixcIlY1RXFIeHpSRDVOdnpN",
                "source": "BellaCarne",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://bellacarne.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab: ecco la ricetta originale! | BellaCarne",
                "link": "https://www.bellacarne.it/blog/ricette-kosher/kebab-ricetta-originale/",
                "tag": "Ricetta",
                "original": "https://www.bellacarne.it/wp-content/uploads/2021/03/kebab-ricetta-originale.jpg",
                "original_width": 1000,
                "original_height": 667,
                "is_product": false
            }
            ,
            {
                "position": 61,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT-y4Q915_sepZZsWylK3mzvNqBTPD_Te595Q&usqp=CAU",
                "related_content_id": "bmFtbDh3X0NYdWRvZk1cIixcImkwaWxxYm1Ya3p3RlNN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=bmFtbDh3X0NYdWRvZk1cIixcImkwaWxxYm1Ya3p3RlNN",
                "source": "Ristorazione Italiana Magazine",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://ristorazioneitalianamagazine.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Planted kebab, la novità sostenibile del Kebhouze di Gianluca Vacchi",
                "link": "https://www.ristorazioneitalianamagazine.it/planted-kebab-based-kebhouze-gianluca-vacchi/",
                "original": "https://www.ristorazioneitalianamagazine.it/CMS/wp-content/uploads/2022/06/kebhouze-Kebab-plant-based-.jpg",
                "original_width": 1200,
                "original_height": 800,
                "is_product": false
            }
            ,
            {
                "position": 62,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSu66nbJ9VRFWY0LY2lj7Uwr5jk-as66dt1RA&usqp=CAU",
                "related_content_id": "czdQVGx2VE16UDFaRk1cIixcInRmdUxiWm5DMUhKeUpN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=czdQVGx2VE16UDFaRk1cIixcInRmdUxiWm5DMUhKeUpN",
                "source": "Ve Eat Cook Bake",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://veeatcookbake.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "The best vegan Kebab you will eat. Almost Oilfree and sugarfree",
                "link": "https://veeatcookbake.com/vegan-doner-kebab/",
                "tag": "Ricetta",
                "original": "https://veeatcookbake.com/wp-content/uploads/2019/09/vegan-doner-kebab-sandwich-3.jpg",
                "original_width": 720,
                "original_height": 1080,
                "is_product": false
            }
            ,
            {
                "position": 63,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ_D3DZN1BlvjzUnF_od8yUFp_pt54sZ-gWQQ&usqp=CAU",
                "related_content_id": "WHFWUHUxT0NwVFBtck1cIixcInVOSkJWQ21CYlBlOThN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=WHFWUHUxT0NwVFBtck1cIixcInVOSkJWQ21CYlBlOThN",
                "source": "Cleanpng",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://it.cleanpng.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Shawarma Doner kebab cucina Vegetariana, patatine fritte - kebab scaricare png - Disegno png trasparente Cucina png scaricare.",
                "link": "https://it.cleanpng.com/png-boib4x/",
                "original": "https://banner2.cleanpng.com/20180326/gsw/kisspng-shawarma-doner-kebab-vegetarian-cuisine-french-fri-kebab-5ab9b8c76426d5.0735333515221209034102.jpg",
                "original_width": 900,
                "original_height": 800,
                "is_product": false
            }
            ,
            {
                "position": 64,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQqjQNl7A1M5zfshORWVLTg2MbiP87IWFyZWw&usqp=CAU",
                "license_details_url": "https://it.123rf.com/license_summary.php",
                "related_content_id": "cnloNVp1T0lYRU5vaE1cIixcIjB1SjBrRno4WUE2YmdN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=cnloNVp1T0lYRU5vaE1cIixcIjB1SjBrRno4WUE2YmdN",
                "source": "123RF",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://it.123rf.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Immagini Stock - Kebab Di Patate Vegetariano Con Cipolla, Prezzemolo E Pane. Image 59631406",
                "link": "https://it.123rf.com/photo_59631406_vegetarian-potato-kebab-with-onion,-parsley-and-bread.html",
                "tag": "Su licenza",
                "original": "https://previews.123rf.com/images/andreyst/andreyst1607/andreyst160701157/59631406-kebab-di-patate-vegetariano-con-cipolla-prezzemolo-e-pane.jpg",
                "original_width": 1300,
                "original_height": 866,
                "is_product": false
            }
            ,
            {
                "position": 65,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFh1SdmnFgZGAM7k41XNDAC6kvD12LToKFMw&usqp=CAU",
                "related_content_id": "dEl6azZmRWx0TVVVaE1cIixcImxwaElHb3Ftd1lxVXJN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=dEl6azZmRWx0TVVVaE1cIixcImxwaElHb3Ftd1lxVXJN",
                "source": "PalermoToday",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://palermotoday.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Il ristorante Jun Kebab with Love di Palermo. La storia",
                "link": "https://www.palermotoday.it/cibo/dove-mangiare/jun-kebab-palermo-storia.html",
                "original": "https://citynews-cibotoday.stgy.ovh/~media/square-hi/48256774786560/il-kebab-du-jun.jpg",
                "original_width": 1200,
                "original_height": 1200,
                "is_product": false
            }
            ,
            {
                "position": 66,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRNRgh3xLqCSVc-cD4Bs0uBkGPMdSPoxaFGZQ&usqp=CAU",
                "related_content_id": "MFg2NlNkTDRfTmRFR01cIixcImpLYk50TGlpTzdYREJN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=MFg2NlNkTDRfTmRFR01cIixcImpLYk50TGlpTzdYREJN",
                "source": "Giulia Nekorkina",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://giulianekorkina.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Aioli, una salsa per il kebab vegetariano - Giulia Nekorkina - Rossa di Sera",
                "link": "https://giulianekorkina.com/2014/08/22/aioli-una-salsa-per-il-kebab-vegetariano/",
                "original": "https://giulianekorkina.com/wp-content/uploads/2020/06/DSC_0845.jpg",
                "original_width": 1339,
                "original_height": 1000,
                "is_product": false
            }
            ,
            {
                "position": 67,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxLwXYqY0WFVe5pjyAXeYGjh2uole4AVSA0Q&usqp=CAU",
                "related_content_id": "b2VyajB5aXJNOUJZUU1cIixcImVPaGQ5ZTJDYktxbE5N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=b2VyajB5aXJNOUJZUU1cIixcImVPaGQ5ZTJDYktxbE5N",
                "source": "Delokos - WordPress.com",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://delokos.wordpress.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegetariano | Delokos",
                "link": "https://delokos.wordpress.com/2009/10/05/kebab-vegetariano/",
                "original": "https://delokos.files.wordpress.com/2009/09/doner-kebap-vegetariano-copia.jpg?w=584",
                "original_width": 584,
                "original_height": 389,
                "is_product": false
            }
            ,
            {
                "position": 68,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWU2CmspiS4HMVHCnpcSGqMYJKB_htxnrdFA&usqp=CAU",
                "related_content_id": "VENmTHpSVzdDX2lZcU1cIixcIk96YzFsbGdzSnJweE5N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=VENmTHpSVzdDX2lZcU1cIixcIk96YzFsbGdzSnJweE5N",
                "source": "Danza de Fogones",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://danzadefogones.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab Vegano Bajo en Grasa - Danza de Fogones",
                "link": "https://danzadefogones.com/kebab-vegano-bajo-en-grasa/",
                "original": "https://danzadefogones.com/wp-content/uploads/2016/06/Kebab-vegano-bajo-en-grasa-2.jpg",
                "original_width": 736,
                "original_height": 1104,
                "is_product": false
            }
            ,
            {
                "position": 69,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJ1UAAj5LQFdvOGtpFxcqLkakLG4hpu7EKxQ&usqp=CAU",
                "related_content_id": "LWVhM1V2MjU5WVpIaU1cIixcIlZYZXJBalNvVnhxY3hN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=LWVhM1V2MjU5WVpIaU1cIixcIlZYZXJBalNvVnhxY3hN",
                "source": "Idea Vegana",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://ideavegana.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegano de soja picante - Receta de Idea Vegana",
                "link": "https://ideavegana.com/kebab-vegano-soja-picante/",
                "original": "https://ideavegana.com/wp-content/uploads/2018/01/receta-kebab-vegano-vegetariano-soja-picante.jpg",
                "original_width": 600,
                "original_height": 450,
                "is_product": false
            }
            ,
            {
                "position": 70,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTVCe9u0BELenOwb8BloVivvwaPPfU30n0lGQ&usqp=CAU",
                "related_content_id": "YjhoSUpiQnhWX2pCWk1cIixcImxhUE56Q3EzNm82WlZN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=YjhoSUpiQnhWX2pCWk1cIixcImxhUE56Q3EzNm82WlZN",
                "source": "PNGEgg",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://pngegg.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Piatto di kebab png | PNGEgg",
                "link": "https://www.pngegg.com/it/search?q=piatto+di+kebab",
                "original": "https://e1.pngegg.com/pngimages/420/735/png-clipart-taco-kebab-kebab-place-restaurant-cuisine-vegetarienne-foodio-prague-plat-thumbnail.png",
                "original_width": 348,
                "original_height": 331,
                "is_product": false
            }
            ,
            {
                "position": 71,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRCt0vVPZVbwLWHKIJvoYQr8TzWMiTWJRk5A&usqp=CAU",
                "related_content_id": "OG42TS1lbzdPRjJ0NE1cIixcIkh6dFVHSG8xT0cwSWVN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=OG42TS1lbzdPRjJ0NE1cIixcIkh6dFVHSG8xT0cwSWVN",
                "source": "franzmagazine",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://franzmagazine.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Il Punto Vegetariano: il Kebab a “Bolzano B” è senza carne | franzmagazine",
                "link": "https://franzmagazine.com/2013/06/28/il-punto-vegetariano-il-kebab-a-bolzano-b-e-senza-carne/",
                "original": "https://franzmagazine.com/wp-content/uploads/2013/06/154.jpg",
                "original_width": 672,
                "original_height": 446,
                "is_product": false
            }
            ,
            {
                "position": 72,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCNREq71YXJI625lKfNRVjnzb6_HsJsII0CQ&usqp=CAU",
                "related_content_id": "bTBuREVZUmF4TU1ad01cIixcImV6OENWbjBlMVFiUWNN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=bTBuREVZUmF4TU1ad01cIixcImV6OENWbjBlMVFiUWNN",
                "source": "Vegolosi",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://vegolosi.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegano di seitan - Ricetta per farlo in casa - Vegolosi.it",
                "link": "https://www.vegolosi.it/ricette-vegane/kebab-vegano-seitan/",
                "tag": "Ricetta",
                "original": "https://www.vegolosi.it/wp-content/uploads/2016/09/kebab-vegan_IMG_0145_650.jpg",
                "original_width": 650,
                "original_height": 350,
                "is_product": false
            }
            ,
            {
                "position": 73,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTK0CcRBi7FDGGXgD-7Nhm36CHjdKeofm4Z4g&usqp=CAU",
                "related_content_id": "b2k4M3k2Q19iRkZZQ01cIixcIlVyeTNuSVljYVNjTEdN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=b2k4M3k2Q19iRkZZQ01cIixcIlVyeTNuSVljYVNjTEdN",
                "source": "La Cucina Italiana",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://lacucinaitaliana.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Mai assaggiato kebab vegetale? | La Cucina Italiana",
                "link": "https://www.lacucinaitaliana.it/gallery/kebab-vegetale-carne-alternativa-planted/",
                "original": "https://media-assets.lacucinaitaliana.it/photos/63d3accc4095617103c9b94d/master/w_1600%2Cc_limit/Planted-Kebab-new_2-1024x1024.png",
                "original_width": 1024,
                "original_height": 1024,
                "is_product": false
            }
            ,
            {
                "position": 74,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_Ri1BCX_cnWdBtSP3jfy8jpvnxy5v4ctaCQ&usqp=CAU",
                "related_content_id": "UFhsaEExakVMQjRwb01cIixcIkdJQkQzXzFGRk82ejlN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=UFhsaEExakVMQjRwb01cIixcIkdJQkQzXzFGRk82ejlN",
                "source": "Deliveroo",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://deliveroo.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Buonissimo Kebab consegna in zona Milano Maggiolina - Ordina su Deliveroo",
                "link": "https://deliveroo.it/it/menu/milano/pasteur/buonissimo-kebab/?day=today&geohash=u0nd9wcgxwfx&time=ASAP",
                "original": "https://rs-menus-api.roocdn.com/images/99c28b51-c494-422b-9a63-37cf010e4b86/image.jpeg",
                "original_width": 1361,
                "original_height": 908,
                "is_product": false
            }
            ,
            {
                "position": 75,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSi6Rxbbw0cqSFlfoWFhGNF13fV9qhAhtixng&usqp=CAU",
                "related_content_id": "a2hETEdpYnN3LTI5Q01cIixcInJTS1h1aEF2OUhYZndN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=a2hETEdpYnN3LTI5Q01cIixcInJTS1h1aEF2OUhYZndN",
                "source": "JUN - Kebab",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://jun-kebab.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Menu - JUN",
                "link": "https://jun-kebab.com/menu/",
                "original": "https://jun-kebab.com/wp-content/uploads/2022/06/JUN-il-nostro-kebab.jpg",
                "original_width": 1400,
                "original_height": 882,
                "is_product": false
            }
            ,
            {
                "position": 76,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQArRWPu3oEpfY_eHw-bTVgbM1DwsKVUkewtw&usqp=CAU",
                "related_content_id": "SkhENVZEZUJNLWJZUU1cIixcIlFlV3hKdjJrYjFsalBN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=SkhENVZEZUJNLWJZUU1cIixcIlFlV3hKdjJrYjFsalBN",
                "source": "www.artumagazine.it",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://artumagazine.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Da Fud Bottega Sicula le nuove proposte veggie e vegan",
                "link": "https://www.artumagazine.it/2022/05/31/da-fud-bottega-sicula-le-nuove-proposte-veggie-e-vegan/",
                "original": "https://www.artumagazine.it/wp-content/uploads/2022/05/fud.jpg",
                "original_width": 852,
                "original_height": 1280,
                "is_product": false
            }
            ,
            {
                "position": 77,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShKYW_gNIOskEcOBNVI11PH2pET-gtb2-Ovg&usqp=CAU",
                "related_content_id": "Y2NUWmZIWnlrelpNX01cIixcIm03Z3NPUUZCNGNGV0FN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=Y2NUWmZIWnlrelpNX01cIixcIm03Z3NPUUZCNGNGV0FN",
                "source": "Enfemenino.com",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://enfemenino.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegano: una delicia rica y saludable",
                "link": "https://www.enfemenino.com/cocina-internacional/kebab-vegano-una-delicia-rica-y-saludable-s3044109.html",
                "original": "https://assets.afcdn.com/story/20190307/1336998_w5616h3159c1cx2901cy1422.jpg",
                "original_width": 5616,
                "original_height": 3159,
                "is_product": false
            }
            ,
            {
                "position": 78,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRl87bqMwhEerK1d37lH3-fe7pxDPWngLHBwg&usqp=CAU",
                "related_content_id": "aDdBc01mN2lFa2xHS01cIixcInc0VlA4TWxCNlFLdE5N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=aDdBc01mN2lFa2xHS01cIixcInc0VlA4TWxCNlFLdE5N",
                "source": "Vegan3000.info",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://vegan3000.info&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Vegan3000.info - Ricetta Vegan - Vegan kebab",
                "link": "https://www.vegan3000.info/r-1672/vegan-kebab",
                "tag": "Ricetta",
                "original": "https://www.vegan3000.info/foto/Foto-1672-02.jpg",
                "original_width": 674,
                "original_height": 433,
                "is_product": false
            }
            ,
            {
                "position": 79,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGFG8MuqdJQQzu6nqV6keXWCICHmDYZ7QuFw&usqp=CAU",
                "related_content_id": "VXVrVjZyNGVYRHVrSk1cIixcImFLcS0tWHU2eXpsbjBN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=VXVrVjZyNGVYRHVrSk1cIixcImFLcS0tWHU2eXpsbjBN",
                "source": "DonnaD",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://donnad.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegetariano fatto in casa | DonnaD",
                "link": "https://www.donnad.it/kebab-vegetariano-ingredienti-ricetta",
                "original": "https://www.donnad.it/sites/default/files/styles/quiz_320x210/public/201819/tacos-di-pollo.jpg?itok=y1g62Xi8",
                "original_width": 320,
                "original_height": 210,
                "is_product": false
            }
            ,
            {
                "position": 80,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbxLVKNS6vBb7g1NL8ZeIQA6NPB-wGsYw0yw&usqp=CAU",
                "related_content_id": "a2wxZkxJU3RHWE5Sck1cIixcIkd2dF91V0lIRmc0UVNN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=a2wxZkxJU3RHWE5Sck1cIixcIkd2dF91V0lIRmc0UVNN",
                "source": "Vandemoortele Professional",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://vandemoorteleprofessional.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Cerca la ricetta | Vandemoortele Professional",
                "link": "https://www.vandemoorteleprofessional.com/it-it/ricette/ricettario",
                "original": "https://dams.vandemoortele.com/transform/e2a1a941-8433-41d0-af53-2a24ffbb2000/52680_fossette_falafel?io=transform%3Afill%2Cwidth%3A1384&format=webp",
                "original_width": 1384,
                "original_height": 922,
                "is_product": false
            }
            ,
            {
                "position": 81,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQLBud9A-Gy0VJuzCvKAzV-ztbRFzHBIiGl1A&usqp=CAU",
                "license_details_url": "https://www.alamy.it/licenses-and-pricing/?v=1",
                "related_content_id": "VklqYUo2dGhiNTlMVU1cIixcIlA4QkEyeUozNlYtMU1N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=VklqYUo2dGhiNTlMVU1cIixcIlA4QkEyeUozNlYtMU1N",
                "source": "Alamy",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://alamy.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Falafel con verdure, salsa al pane pita, panino kebab vegetariano. Sfondo nero. Vista dall'alto Foto stock - Alamy",
                "link": "https://www.alamy.it/falafel-con-verdure-salsa-al-pane-pita-panino-kebab-vegetariano-sfondo-nero-vista-dall-alto-image397869783.html",
                "tag": "Su licenza",
                "original": "https://c8.alamy.com/compit/2e38ey3/falafel-con-verdure-salsa-al-pane-pita-panino-kebab-vegetariano-sfondo-nero-vista-dall-alto-2e38ey3.jpg",
                "original_width": 1300,
                "original_height": 954,
                "is_product": false
            }
            ,
            {
                "position": 82,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRb_Vlqbvl9w5zQbsWOy51f6IA63r2wt9QyOw&usqp=CAU",
                "related_content_id": "cGU3X2cwNEFGTGtCMU1cIixcIjlmeHRSNjdwT1dRT05N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=cGU3X2cwNEFGTGtCMU1cIixcIjlmeHRSNjdwT1dRT05N",
                "source": "la Repubblica",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://repubblica.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Nel Ghetto di Roma il kebab d'autore di Oriental Fonzie - la Repubblica",
                "link": "https://www.repubblica.it/sapori/2020/08/24/news/roma_recensione_locale_oriental_fonzie-262179647/",
                "original": "https://www.repstatic.it/content/nazionale/img/2020/07/17/122429548-84e8f2ca-0ca2-4650-9bbe-6c2f09cdf1b9.jpg",
                "original_width": 560,
                "original_height": 315,
                "is_product": false
            }
            ,
            {
                "position": 83,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRvefbmk9S8_IrodjrVuSiqHZGVf2wJkCldKQ&usqp=CAU",
                "related_content_id": "N1NDM2txeUpmR0NMV01cIixcIlJxYnFGXzdQZmdFdGZN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=N1NDM2txeUpmR0NMV01cIixcIlJxYnFGXzdQZmdFdGZN",
                "source": "Sale&Pepe",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://salepepe.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Bocconcini di kebab di seitan | Sale&Pepe",
                "link": "https://www.salepepe.it/ricette/secondi/bocconcini-kebab-seitan/",
                "tag": "Ricetta",
                "original": "https://www.salepepe.it/files/2016/07/Bocconcini-di-kebab-di-seitan--1140x636.jpg",
                "original_width": 1140,
                "original_height": 636,
                "is_product": false
            }
            ,
            {
                "position": 84,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCVS8ZpaVCm4bGIpTylVm2ruOq-pMNcf1wKg&usqp=CAU",
                "related_content_id": "dGxibnVPVUtaQzNSeU1cIixcImh2eDlrZWtrVzdSSV9N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=dGxibnVPVUtaQzNSeU1cIixcImh2eDlrZWtrVzdSSV9N",
                "source": "abillion",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://abillion.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Anatolia - Arabian Kebab Siracusa, Italy Kebab vegetariano Review | abillion",
                "link": "https://www.abillion.com/reviews/621401ae2b88d8009e5f6fe1",
                "original": "https://imagedelivery.net/olI9wp0b6luWFB9nPfnqjQ/res/abillionveg/image/upload/e9zgju3fg9eqieuwaa3q/1645478257.jpg/w=720",
                "original_width": 720,
                "original_height": 720,
                "is_product": false
            }
            ,
            {
                "position": 85,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSqczHX0KTd-m5IFOWFBe0TXKrXrH8YoBwbZw&usqp=CAU",
                "related_content_id": "dTRQUkdhbktKYjNuN01cIixcIkMwaGFPWE0zQ01vcmpN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=dTRQUkdhbktKYjNuN01cIixcIkMwaGFPWE0zQ01vcmpN",
                "source": "Vecteezy",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://it.vecteezy.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "doner kebab vegetale shawarma burrito ripieno pita vegetariano vegetariano 5443361 Stock Photo su Vecteezy",
                "link": "https://it.vecteezy.com/foto/5443361-doner-kebab-vegetable-shawarma-burrito-filling-veggie-pita-vegetariano",
                "original": "https://static.vecteezy.com/ti/foto-gratuito/p2/5443361-doner-kebab-vegetable-shawarma-burrito-filling-veggie-pita-vegetariano-foto.jpg",
                "original_width": 2940,
                "original_height": 1960,
                "is_product": false
            }
            ,
            {
                "position": 86,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS0Z6eLlNxVSo0uDL5PCnm7-yN6G063EiYiTQ&usqp=CAU",
                "related_content_id": "WDlRNGtiYkdFQVBBZ01cIixcIlRGbnE2UF9iQXJ0YTBN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=WDlRNGtiYkdFQVBBZ01cIixcIlRGbnE2UF9iQXJ0YTBN",
                "source": "Nueva Mujer",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://nuevamujer.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Rápido y simple: ¡prepara un Kebab vegetariano! - Sabrosía",
                "link": "https://www.nuevamujer.com/lifestyle/2013/06/20/rapido-y-simple-prepara-un-kebab-vegetariano.html",
                "original": "https://www.nuevamujer.com/resizer/c0OD9mehyteZ0qvsdezzMBMFpn4=/800x0/filters:format(jpg):quality(70)/cloudfront-us-east-1.images.arcpublishing.com/metroworldnews/JYU2ZNXXCRGVPAZBRY5JB32GYM.jpg",
                "original_width": 800,
                "original_height": 424,
                "is_product": false
            }
            ,
            {
                "position": 87,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTaeCT8NDDTpc6ANyReGImR3JgycIPKJor1Iw&usqp=CAU",
                "related_content_id": "dDhXc3VlN21sdXRpY01cIixcIkN2NWpHNnFEZEh5MkdN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=dDhXc3VlN21sdXRpY01cIixcIkN2NWpHNnFEZEh5MkdN",
                "source": "Cleanpng",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://it.cleanpng.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Vegetariano doner kebab Wrap di Pollo cucina la situazione - Doner kebab scaricare png - Disegno png trasparente Cibo png scaricare.",
                "link": "https://it.cleanpng.com/png-zei7et/",
                "original": "https://banner2.cleanpng.com/20180729/bzt/kisspng-vegetarian-cuisine-doner-kebab-wrap-drm-chicke-doner-kebab-5b5e54991e1412.4748960815329086971232.jpg",
                "original_width": 900,
                "original_height": 400,
                "is_product": false
            }
            ,
            {
                "position": 88,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzWhzHw3qqKS6xalwWf95_YQ_lMvHdMT1xlw&usqp=CAU",
                "related_content_id": "ckZ2RTJCM0V3Rm0wSE1cIixcInVmZzB2NTFoSGJFTWxN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=ckZ2RTJCM0V3Rm0wSE1cIixcInVmZzB2NTFoSGJFTWxN",
                "source": "Glovo",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://glovoapp.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Consegna di cibo Vegetariano a domicilio a Bisceglie | Ordina ora online con Glovo",
                "link": "https://glovoapp.com/it/it/bisceglie/ristoranti_1/vegetariano_34795/",
                "original": "https://images.deliveryhero.io/image/stores-glovo/stores/98a8fde14bc53f0bdbabb87227c76bca89c754ea88216fb41859cb637003163c?t=W3siYXV0byI6eyJxIjoibG93In19LHsicmVzaXplIjp7Im1vZGUiOiJmaWxsIiwiYmciOiJ0cmFuc3BhcmVudCIsIndpZHRoIjoyOTQsImhlaWdodCI6MTYwfX1d",
                "original_width": 294,
                "original_height": 160,
                "is_product": false
            }
            ,
            {
                "position": 89,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR13hJk39LIfPy85AxQZYae8Q_IPQugPNa1IA&usqp=CAU",
                "license_details_url": "https://www.dreamstime.com/about-stock-image-licenses",
                "related_content_id": "QjdsRmFHLWcyZjcxak1cIixcIjlzMUl1eEtpOUlOWlZN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=QjdsRmFHLWcyZjcxak1cIixcIjlzMUl1eEtpOUlOWlZN",
                "source": "Dreamstime",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://es.dreamstime.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab Vegetariano Y Kebab Con Dieta En Salsa Kebab Imagen de archivo - Imagen de brocheta, dieta: 230244459",
                "link": "https://es.dreamstime.com/kebab-vegetariano-y-con-dieta-en-salsa-vegetal-br%C3%B3coli-verduras-de-ocraroato-brocheta-image230244459",
                "tag": "Su licenza",
                "original": "https://thumbs.dreamstime.com/z/kebab-vegetariano-y-con-dieta-en-salsa-vegetal-br%C3%B3coli-verduras-de-ocraroato-brocheta-230244459.jpg",
                "original_width": 1600,
                "original_height": 1157,
                "is_product": false
            }
            ,
            {
                "position": 90,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT56EpuRLIHSo_35ZvUVTDwhmXkVPBTzO8DOw&usqp=CAU",
                "related_content_id": "OVZTQTVQUXRlWEQ1N01cIixcImRXTTUyTmZMUEp1bTZN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=OVZTQTVQUXRlWEQ1N01cIixcImRXTTUyTmZMUEp1bTZN",
                "source": "Envato Elements",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://elements.envato.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegetariano Fotos de Stock e Imágenes, todas libres de regalías - Envato Elements",
                "link": "https://elements.envato.com/es/photos/kebab+vegetariano",
                "original": "https://envato-shoebox-0.imgix.net/ef9e/330b-b84d-4308-8d76-7b747695a9c1/DSC_1411.JPG?auto=compress%2Cformat&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark2.png&w=700&fit=max&markalign=center%2Cmiddle&markalpha=18&s=f54e7015503f6375cbf0c911e90dca55",
                "original_width": 700,
                "original_height": 466,
                "is_product": false
            }
            ,
            {
                "position": 91,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSDH8igLiNNnX2kOqW-wHvPMOqLBI0ftcnuVw&usqp=CAU",
                "related_content_id": "bnRtc0NBLWRCenc3Y01cIixcIlVtWkJYWHFnd3pPcnFN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=bnRtc0NBLWRCenc3Y01cIixcIlVtWkJYWHFnd3pPcnFN",
                "source": "Sfizi & Vizi",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://sfizievizi.blogspot.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Sfizi & Vizi: Piadina Arrotolabile con crema di pistacchi e pinoli ovvero il mio simil-kebab vegetariano",
                "link": "http://sfizievizi.blogspot.com/2014/02/piadina-arrotolabile-con-crema-di.html",
                "original": "http://1.bp.blogspot.com/-Y-h8cggZSqE/UwpsHy1ItmI/AAAAAAAAKlY/DmPkAvEw454/s1600/1.jpg",
                "original_width": 1391,
                "original_height": 1046,
                "is_product": false
            }
            ,
            {
                "position": 92,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShTnV89sn_pt9bd2I2v-ZUyjah_tCKYdltcQ&usqp=CAU",
                "related_content_id": "RFctREdNMm5pdHpJRE1cIixcIk1ocG1uUU1ReC1lUmNN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=RFctREdNMm5pdHpJRE1cIixcIk1ocG1uUU1ReC1lUmNN",
                "source": "Tripadvisor",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://tripadvisor.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab vegetariano, falafel con hummus, riso con crema deliziosa di verdure - Foto di Kirkuk Kaffe, Torino - Tripadvisor",
                "link": "https://www.tripadvisor.it/LocationPhotoDirectLink-g187855-d942382-i128341198-Kirkuk_Kaffe-Turin_Province_of_Turin_Piedmont.html",
                "original": "https://media-cdn.tripadvisor.com/media/photo-s/07/a6/54/ce/kebab-vegetariano-falafel.jpg",
                "original_width": 253,
                "original_height": 450,
                "is_product": false
            }
            ,
            {
                "position": 93,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQq8uAtpItVFjH01dDMRSMmlqWiCjCRsLj4YA&usqp=CAU",
                "related_content_id": "andOWFhkaHBDbXNMWE1cIixcIklpODVRWmNjek9sQm1N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=andOWFhkaHBDbXNMWE1cIixcIklpODVRWmNjek9sQm1N",
                "source": "Dissapore",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://dissapore.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab: ricetta, com'è fatto, migliori kebabberie",
                "link": "https://www.dissapore.com/grande-notizia/kebab-ricetta-come-fatto/",
                "original": "https://images.dissapore.com/wp-content/uploads/2015/02/Kebab-Al-Mercato.jpg?width=660&height=400&quality=75",
                "original_width": 400,
                "original_height": 400,
                "is_product": false
            }
            ,
            {
                "position": 94,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSO73Nfa1yOn2vpRMUpDMVmC3zlUOaL550hPg&usqp=CAU",
                "related_content_id": "MXVhY0hiUGFNZkxKME1cIixcIjVZMXFQeGh5Q2lhYzVN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=MXVhY0hiUGFNZkxKME1cIixcIjVZMXFQeGh5Q2lhYzVN",
                "source": "Yum Vegan Lunch Ideas",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://yumveganlunchideas.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Vegan Shawarma Sandwich | Vegan Doner Kebab Recipe",
                "link": "https://yumveganlunchideas.com/vegan-shawarma-vegan-doner-kebab-recipe/",
                "tag": "Ricetta",
                "original": "https://yumveganlunchideas.com/wp-content/uploads/2019/11/Vegan-Sharwarma-Doner-Kebab-7-scaled.jpg",
                "original_width": 2560,
                "original_height": 1957,
                "is_product": false
            }
            ,
            {
                "position": 95,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSXrTh8J2NxPFFK33mgpQFh2HAgL5PEWfAjzA&usqp=CAU",
                "related_content_id": "a05NMEJFMFltR2x3cE1cIixcIkdsZ0tMQ2VSLUtET1JN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=a05NMEJFMFltR2x3cE1cIixcIkdsZ0tMQ2VSLUtET1JN",
                "source": "Il Cucchiaio Verde",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://ilcucchiaioverde.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Kebab veg - Il Cucchiaio Verde",
                "link": "https://www.ilcucchiaioverde.com/kebab-veg/",
                "tag": "Ricetta",
                "original": "https://www.ilcucchiaioverde.com/wp-content/uploads/2023/09/kebab_veg_pin.jpg",
                "original_width": 735,
                "original_height": 1102,
                "is_product": false
            }
            ,
            {
                "position": 96,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQYHHKP5zt41Fp2ylN32wWrgwLpbt4UCQ2vvQ&usqp=CAU",
                "related_content_id": "bC1aRmMzNWQ3a3BEZ01cIixcIkRtNkk0ZU9wQm9waXJN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=bC1aRmMzNWQ3a3BEZ01cIixcIkRtNkk0ZU9wQm9waXJN",
                "source": "TikTok",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://tiktok.com&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "E se ti dicessi che quella non e' carne, ma farina di piselli?🍃❤️ #ke... | TikTok",
                "link": "https://www.tiktok.com/@kebhouze/video/7204789530258377990",
                "original": "https://www.tiktok.com/api/img/?itemId=7204789530258377990&location=0&aid=1988",
                "original_width": 720,
                "original_height": 1280,
                "is_product": false
            }
            ,
            {
                "position": 97,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTV-aJYDZcrZ9OLcLafb4XIMLG5BpYln-UmYg&usqp=CAU",
                "related_content_id": "UG54T1A5cUNfeHRVMk1cIixcIkNjWmYwcnhTbjBaMEFN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=UG54T1A5cUNfeHRVMk1cIixcIkNjWmYwcnhTbjBaMEFN",
                "source": "Agrodolce",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://agrodolce.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Come farcire un panino kebab - Agrodolce",
                "link": "https://www.agrodolce.it/2023/06/14/come-farcire-panino-kebab/",
                "original": "https://cdn.agrodolce.it/7WE2yZ0u2Sw5oSa0Ev0TPYjcU8A=/1200x800/smart/https://www.agrodolce.it/app/uploads/2017/01/shutterstock_432817423.jpg",
                "original_width": 1200,
                "original_height": 800,
                "is_product": false
            }
            ,
            {
                "position": 98,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ-LMS2hIQCxwuNYbQ4ykDXIY7F8GPGNw6Izw&usqp=CAU",
                "related_content_id": "Q0FmRl9OODd4VERXOE1cIixcIklhWUladGM5SDluZ0pN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=Q0FmRl9OODd4VERXOE1cIixcIklhWUladGM5SDluZ0pN",
                "source": "Paneangeli",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://paneangeli.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Ricetta Kebab | Paneangeli",
                "link": "https://paneangeli.it/ricetta/kebab",
                "tag": "Ricetta",
                "original": "https://recipesblob.paneangeli.it/assets/43df75bae33b4c71a9e66072f96b6f0f/1272x764/kebabjpg.jpg",
                "original_width": 1272,
                "original_height": 764,
                "is_product": false
            }
            ,
            {
                "position": 99,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ07QpfvrMKrdfZfmMO_6Mkake-Sn0eObx8yQ&usqp=CAU",
                "related_content_id": "UDZoMW9xazhNaHpRS01cIixcIko5Nnc3LVp5VjhBbmdN",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=UDZoMW9xazhNaHpRS01cIixcIko5Nnc3LVp5VjhBbmdN",
                "source": "rustic shaorma",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://rusticshaorma.it&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "SHAORMA ARROTOLATO VEGETARIANO — rustic shaorma",
                "link": "https://www.rusticshaorma.it/prodotti/shaorma-arrotolato-vegetariano",
                "original": "http://images.squarespace-cdn.com/content/v1/5e9f5aa5f8e1dd3c06a93fa2/1604134329443-LGQBV4RXRK5R6YVGLJGJ/SHAORMA-VEGET.jpg",
                "original_width": 2500,
                "original_height": 1667,
                "is_product": false
            }
            ,
            {
                "position": 100,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ9Wbgilrzb8yxYXYZ4N4uBoAN8DV34tF_Q8A&usqp=CAU",
                "related_content_id": "eGV2NnRrQzFqZTN6Qk1cIixcImRMd1RoS242MV9nWU9N",
                "serpapi_related_content_link": "https://serpapi.com/search.json?engine=google_images_related_content&gl=it&hl=it&q=Kebab+vegetariano&related_content_id=eGV2NnRrQzFqZTN6Qk1cIixcImRMd1RoS242MV9nWU9N",
                "source": "Le Garb",
                "source_logo": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://legarb.com.br&client=VFE&size=16&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2",
                "title": "Le Garb: Falafel - Koftas e kebab vegetariano",
                "link": "http://www.legarb.com.br/2015/06/falafel-koftas-e-kebab-vegetariano.html",
                "original": "http://3.bp.blogspot.com/-1PaBSXfUp9U/VXLvoRzfTYI/AAAAAAAAQuQ/9ng0PcdSzk0/s1600/kebab%2Bfalafel.jpg",
                "original_width": 960,
                "original_height": 541,
                "is_product": false
            }
        ]
        ,
        "related_searches":
        [
            {
                "link": "https://www.google.it/search?q=kebab+animale&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEI0B",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=kebab+animale",
                "query": "kebab animale",
                "highlighted_words":
                [
                    "animale"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT66zye-2aFA5MfFZD1AyBK5eLLpjem-TVSaWfaCQ99IAVNRUVPADLMA4w&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=kebab+underwater&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEI8B",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=kebab+underwater",
                "query": "kebab underwater",
                "highlighted_words":
                [
                    "underwater"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ2NInTC-w12CIh0TgedkRz2IpNeFCAISv3ZKNk9vhq9BvLdLqUtXxkFno&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=kebab+sottomarino&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEJEB",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=kebab+sottomarino",
                "query": "kebab sottomarino",
                "highlighted_words":
                [
                    "sottomarino"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRg4W-SGAaX71Ew-8auOdxfC9yRWg2bpCfymJeBFLq_FgVaur1ZVr9C3mk&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=kebab+origine&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEMoB",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=kebab+origine",
                "query": "kebab origine",
                "highlighted_words":
                [
                    "origine"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSNtwQ1yHMCSzHgA4KSN-i5fijlD4INGakKW3YFhA3BXRSXQl7hC8QWrgg&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=kebab+ingredienti&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEMwB",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=kebab+ingredienti",
                "query": "kebab ingredienti",
                "highlighted_words":
                [
                    "ingredienti"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTyO7ZDhvioJxgIK2CUuraU2Da6huknDX1cJQj8-EIp64VTMzU6jXIXu8&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=kebab+originale&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEM4B",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=kebab+originale",
                "query": "kebab originale",
                "highlighted_words":
                [
                    "originale"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4U1jQ1GbnTCy4dpIjohB7C85UODIzG4sbIwE_sMIcDP3M6JTt3wwSAFk&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=kebab+marino&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEIYC",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=kebab+marino",
                "query": "kebab marino",
                "highlighted_words":
                [
                    "marino"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSzjiKol8eZselQJSvlGAPuBGC-xMoRD5cUzvqXiXaTuxibeugKkrJOX48&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=panino+kebab&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEIgC",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=panino+kebab",
                "query": "panino kebab",
                "highlighted_words":
                [
                    "panino"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRCgUJRzdqSYjOuRv8lZKLVREJeFIKlM09fzgiCQphJmvDWYeeTVlz_W-c&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=carne+kebab&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEIoC",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=carne+kebab",
                "query": "carne kebab",
                "highlighted_words":
                [
                    "carne"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgoCvHA9cqPeFhoFINRt4aalD2zGOZdP7SFRsMRO9LkCF7633JqzRA3fo&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=kebab+in+acqua&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEMMC",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=kebab+in+acqua",
                "query": "kebab in acqua",
                "highlighted_words":
                [
                    "in acqua"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTjaqL0XN9eAbEkA3BwMRGUP2GnU2yzsKgGZthUwh--rrV16RFvbGUPtxo&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=kebab+intero&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEMUC",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=kebab+intero",
                "query": "kebab intero",
                "highlighted_words":
                [
                    "intero"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRqVnchNVUBA1Mb_Mk8WgJkbLrRX4nCHOKidWpqEmlQ7ACmOuTDYIqIVNs&usqp=CAU"
            }
            ,
            {
                "link": "https://www.google.it/search?q=kebab+piadina&tbm=isch&hl=it&gl=it&sa=X&ved=2ahUKEwj6x7DG37WDAxVYNWIAHQ5FA0kQrNwCKAB6BQgBEMcC",
                "serpapi_link": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=kebab+piadina",
                "query": "kebab piadina",
                "highlighted_words":
                [
                    "piadina"
                ]
                ,
                "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsdEvpRRKEaKE-w6Oy5ToPJJsX_2yEacWL6hISshBwnxL1qYSJylW9qWw&usqp=CAU"
            }
        ]
        ,
        "serpapi_pagination":
        {
            "current": 0,
            "next": "https://serpapi.com/search.json?device=desktop&engine=google_images&gl=it&google_domain=google.it&hl=it&ijn=1&location=Metropolitan+City+of+Florence%2C+Tuscany%2C+Italy&q=Kebab+vegetariano"
        }
    }
               """);

external_blueprint = Blueprint(
    'external',
    __name__,
    url_prefix=BASE_PATH + '/external'
)

_image_schema = ImageSchema()

@external_blueprint.route('/image_search')
@jwt_required
def image_search():
    serpApiResp = _mock;

    _logger.debug("SerpAPI returns: %s", serpApiResp)

    if(serpApiResp['search_metadata']['status'] != "Success"):
        raise ServiceUnavailable('image search service failed to retrieve results') 
    
    imageResults = serpApiResp["images_results"];

    schema = ImageSchema(many=True)
    
    return jsonify(schema.dump(imageResults)), 200

