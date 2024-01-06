from typing import Any, Optional
import certifi
import scrapy
import logging
import json
import time
import crypt

from os import getenv
from scrapy.shell import inspect_response
from scrapy.http import Response
from scrapy.spiders import SitemapSpider
from scrapy.crawler import CrawlerProcess
from scrapy.spidermiddlewares.httperror import HttpError
from recipe_scrapers import scrape_me
from mongoengine import *

from weekly_menu.job.crawler import RecipeSites
from weekly_menu.webapp.api.models.recipe import ScrapedRecipes, IngredientGroup


CRAWLER_DATA_BASE_PATH = "crawler/"


class RecipeSitemapSpider(SitemapSpider):
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    }

    DEFAULT_REQUEST_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "it-IT,en;q=0.8,it;q=0.5,en-US;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.fattoincasadabenedetta.it/recipe-sitemap.xml",
        "DNT": "1",
        "Alt-Used": "www.fattoincasadabenedetta.it",
        "Connection": "keep-alive",
        "Cookie": "euconsent-v2=CP3wTQAP3wTQAFgAGAITAdEsAP_gAAAAABCYJyNX_H__bX9r8Xr36ft0eY1f99j77sQxBhfJk-4FyLvW_JwX32EyNA26tqYKmRIEu3ZBIQFlHJHURVigaogVrzHsYkGcgTNKJ6BkgFMRY2dYCF5vmYtj-QKY5_p_d3f52T-9_dv83dzzz8Vnv3e5fmclcKCdQ58tDfn_bRKb-5IO9-78v4v09t_rk2_eTVn_tevr7B-uft-7_XV-9_fEGqB6AC4AHAAPwApgB-AGWAM2AiwCLgEpAJoAVAAz4BrwDpAH2AR4AlUBMgCZwFhALvAX0AwQBgwDIQGjANNAaqA2gBvgDggHHgOdAc-A6wB2wDuQHkgPtAfsBBECCgEMwI0gR0AjsBH0CREEkQSSAkoBKOCWYJaAS4AmCBMMCY4EyQJmATSAm-EFAAoJABgACINQaADAAEQahEAGAAIg1CoAMAARBqGQAYAAiDUOgAwABEGohABgACINRKADAAEQaikAGAAIg1FoAMAARBqA.f_wAAAAAAAAA; pubtech-cmp-pcstring=7-1XX",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    def __init__(
        self,
        name: str,
        url: str,
        start_urls: list,
        search_path: list,
        depth=0,
        cookies_enabled=True,
        random_delay_sec=0,
        required_recipe_fields=[],
        **kwargs: Any
    ):
        if start_urls == None or len(start_urls) == 0:
            self.sitemap_urls = [url]
        else:
            self.sitemap_urls = start_urls

        self.url = url

        self.sitemap_follow = search_path

        self.download_delay = 0 if random_delay_sec == None else random_delay_sec

        self.required_recipe_fields = required_recipe_fields

        if self.custom_settings == None:
            self.custom_settings = {
                "COOKIES_ENABLED": True if cookies_enabled == None else cookies_enabled
            }
        else:
            self.custom_settings["COOKIES_ENABLED"] = (
                True if cookies_enabled == None else cookies_enabled
            )

        if self.custom_settings == None:
            self.custom_settings = {"DEPTH_LIMIT": 0 if depth == None else depth}
        else:
            self.custom_settings["DEPTH_LIMIT"] = 0 if depth == None else depth

        super().__init__(name + "_sitemap_spider", **kwargs)

    def parse(self, response: Response):
        self.logger.debug("parsing response: %s", response.url)

        recipe = None
        try:
            recipe = scrape_me(response.url)
        except:
            self.logger.warning("failed to scrape recipe from: %s", response.url)

        if recipe != None:
            self.logger.info("recipe found in: %s", response.url)
            self.logger.debug(recipe.to_json())

            doc = None
            try:
                doc = ScrapedRecipes(
                    host=recipe.host(),
                    title=recipe.title(),
                    total_time=recipe.total_time(),
                    image=recipe.image(),
                    ingredients=recipe.ingredients(),
                    ingredient_groups=map(
                        lambda ig: IngredientGroup(
                            purpose=ig.purpose, ingredients=ig.ingredients
                        ),
                        recipe.ingredient_groups(),
                    ),
                    instructions=recipe.instructions(),
                    instructions_list=recipe.instructions_list(),
                    links=recipe.links(),
                    servings=recipe.yields(),
                    nutrients=recipe.nutrients(),  # if available
                    canonical_url=recipe.canonical_url(),  # also not always available
                    url=response.url,
                )
                self.logger.info("scraped recipe from: %s", response.url)
            except Exception as e:
                self.logger.exception(
                    "failed to scrape recipe '%s' from remote", response.url
                )

            if doc != None:
                try:
                    doc.save()
                    self.logger.debug("recipe '%s' saved to db", response.url)
                except:
                    self.logger.exception(
                        "failed to save recipe '%s' to db", response.url
                    )

        self.logger.debug("parsed response: %s", response.url)


class RecipeSpider(scrapy.Spider):
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
    }

    DEFAULT_REQUEST_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "it-IT,en;q=0.8,it;q=0.5,en-US;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.fattoincasadabenedetta.it/recipe-sitemap.xml",
        "DNT": "1",
        "Alt-Used": "www.fattoincasadabenedetta.it",
        "Connection": "keep-alive",
        "Cookie": "euconsent-v2=CP3wTQAP3wTQAFgAGAITAdEsAP_gAAAAABCYJyNX_H__bX9r8Xr36ft0eY1f99j77sQxBhfJk-4FyLvW_JwX32EyNA26tqYKmRIEu3ZBIQFlHJHURVigaogVrzHsYkGcgTNKJ6BkgFMRY2dYCF5vmYtj-QKY5_p_d3f52T-9_dv83dzzz8Vnv3e5fmclcKCdQ58tDfn_bRKb-5IO9-78v4v09t_rk2_eTVn_tevr7B-uft-7_XV-9_fEGqB6AC4AHAAPwApgB-AGWAM2AiwCLgEpAJoAVAAz4BrwDpAH2AR4AlUBMgCZwFhALvAX0AwQBgwDIQGjANNAaqA2gBvgDggHHgOdAc-A6wB2wDuQHkgPtAfsBBECCgEMwI0gR0AjsBH0CREEkQSSAkoBKOCWYJaAS4AmCBMMCY4EyQJmATSAm-EFAAoJABgACINQaADAAEQahEAGAAIg1CoAMAARBqGQAYAAiDUOgAwABEGohABgACINRKADAAEQaikAGAAIg1FoAMAARBqA.f_wAAAAAAAAA; pubtech-cmp-pcstring=7-1XX",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    def __init__(
        self,
        name: str,
        url: str,
        start_urls: list,
        search_path: list,
        depth=0,
        cookies_enable=True,
        random_delay_sec=0,
        required_recipe_fields=[],
        **kwargs: Any
    ):
        if start_urls == None or len(start_urls) == 0:
            self.start_urls = [url]
        else:
            self.start_urls = start_urls

        self.url = url

        self.search_path = search_path

        self.download_delay = 0 if random_delay_sec == None else random_delay_sec

        self.required_recipe_fields = required_recipe_fields

        if self.custom_settings == None:
            self.custom_settings = {}

        self.custom_settings["COOKIES_ENABLED"] = (
            True if cookies_enable == None else cookies_enable
        )

        self.custom_settings["DEPTH_LIMIT"] = 0 if depth == None else depth

        self.custom_settings["JOBDIR"] = "{}}/{}".format(CRAWLER_DATA_BASE_PATH, name)

        super().__init__(name + "_spider", **kwargs)

    def start_requests(self):
        for url in self.start_urls:
            self.logger.info("start scraping from url: %s", url)
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errback)

    def errback(self, failure):
        # log all errback failures,
        # in case you want to do something special for some errors,
        # you may need the failure's type
        self.logger.error(repr(failure))

        # if isinstance(failure.value, HttpError):
        if failure.check(HttpError):
            # you can get the response
            response = failure.value.request
            self.logger.error("HttpError on %s\n%s", response.url, response.text)

        # elif isinstance(failure.value, DNSLookupError):
        # elif failure.check(DNSLookupError):
        #    # this is the original request
        #    request = failure.request
        #    self.logger.error('DNSLookupError on %s', request.url)

        # elif isinstance(failure.value, TimeoutError):
        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error("TimeoutError on %s", request.url)

    def parse(self, response: Response):
        self.logger.debug("parsing response: %s", response.url)

        recipe = None
        try:
            recipe = scrape_me(response.url)
        except:
            self.logger.warning("failed to scrape recipe from: %s", response.url)

        if recipe != None:
            self.logger.info("recipe found in: %s", response.url)
            self.logger.debug(recipe.to_json())

            json_recipe = recipe.to_json()

            current_fields = json_recipe.keys()
            valid_recipe = True
            for required_field in self.required_recipe_fields:
                if (
                    required_field not in current_fields
                    or json_recipe[required_field] == None
                ):
                    valid_recipe = False
                    break

            if valid_recipe == True:
                # doc = None
                try:
                    ScrapedRecipes._get_collection().insert_one(json_recipe)
                    # doc = ScrapedRecipes(
                    #  host=recipe.host(),
                    #  title=recipe.title(),
                    #  total_time = recipe.total_time(),
                    #  image = recipe.image(),
                    #  ingredients = recipe.ingredients(),
                    #  ingredient_groups = map(lambda ig: IngredientGroup(purpose=ig.purpose, ingredients=ig.ingredients), recipe.ingredient_groups()),
                    #  instructions = recipe.instructions(),
                    #  instructions_list = recipe.instructions_list(),
                    #  links = recipe.links(),
                    #  servings = recipe.yields(),
                    #  nutrients = recipe.nutrients(),  # if available
                    #  canonical_url = recipe.canonical_url(),  # also not always available

                    #  url=response.url
                    # )
                    self.logger.info("scraped recipe from: %s", response.url)
                except Exception as e:
                    self.logger.exception(
                        "failed to scrape recipe '%s' from remote", response.url
                    )

                # if(doc != None):
                #  try:
                #    doc.save()
                #    self.logger.debug("recipe '%s' saved to db", response.url)
                #  except:
                #    self.logger.exception("failed to save recipe '%s' to db", response.url)
            else:
                self.logger.warning(
                    "scraped recipe from url: %s is invalid", response.url
                )

        # TODO handle multiple search path
        next_pages = (
            response.css("a[href*='{}']".format(self.search_path[0]))
            .xpath("@href")
            .getall()
        )

        if next_pages is not None and len(next_pages) > 0:
            for next_page in next_pages:
                yield response.follow(next_page, self.parse)

        return json_recipe

        self.logger.debug("parsed response: %s", response.url)


connect(
    host=getenv("JOB_DB_URL"),
    tlsCAFile=certifi.where(),
)

for rs in RecipeSites.objects:
    print("===", rs.url, "===")
    if rs.enabled == True:
        process = CrawlerProcess()
        cls = RecipeSitemapSpider if rs.crawler_type == "sitemap" else RecipeSpider
        process.crawl(
            cls,
            rs.names,
            url=rs.url,
            start_urls=list(rs.start_urls),
            search_path=list(rs.search_path),
            depth=rs.depth,
            cookies_enabled=rs.cookies_enabled,
            random_delay_sec=rs.random_delay_sec,
            required_recipe_fields=list(rs.required_recipe_fields),
        )
        process.start()
