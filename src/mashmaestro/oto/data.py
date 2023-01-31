# load grains set
import csv
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from pybeerxml.parser import Parser
from selenium import webdriver

from mashmaestro.language import unique_words
from mashmaestro.logger import logger
from mashmaestro.paths import bot3_pickle

from .paths import bot2_pickle, bot_path, download_path, kaggle_csv, processed_path


def get_brewers_friend_ids():
    # recipeData = "https://www.kaggle.com/datasets/jtrofe/beer-recipes?resource=download"
    # styleData = "https://www.kaggle.com/datasets/jtrofe/beer-recipes?resource=download"
    bfriendid = []
    with open(kaggle_csv, errors="replace") as recipes:
        recipes = recipes.readlines()
    spamreader = csv.reader(recipes, delimiter=",")
    next(spamreader)  # header
    for row in spamreader:
        url = row[2]  # URL
        path = url.split("/")
        bfriendid.append(path[4])
    return bfriendid


def new_chrome_browser(headless=True, downloads=None):
    """Helper function that creates a new Selenium browser"""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("headless")
    if downloads is not None:
        prefs = {}
        os.makedirs(downloads, exist_ok=True)
        prefs["profile.default_content_settings.popups"] = 0
        prefs["download.default_directory"] = downloads
        options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(options=options)
    return browser


def download_recipes(bfriendids):
    browser = new_chrome_browser(downloads=download_path)

    for id in bfriendids:
        browser.get(f"https://www.brewersfriend.com/homebrew/recipe/beerxml1.0/{id}")


def beer_xml():
    try1 = Path(download_path)
    bxmls = try1.iterdir()
    parser = Parser()
    grains_set = set()
    hops_set = set()
    yeasts_set = set()
    recipe_mapping = {}
    for b in bxmls:
        recipes = parser.parse(b)
        grains = [grain.name for grain in recipes[0].fermentables]
        hops = [hop.name for hop in recipes[0].hops]
        yeasts = [yeast.name for yeast in recipes[0].yeasts]
        gw, hw, yw = unique_words(grains=grains, hops=hops, yeasts=yeasts)
        grains_set.update(gw)
        hops_set.update(hw)
        yeasts_set.update(yw)
        recipe_mapping[b] = dict(grains=gw, hops=hw, yeasts=yw)
    return grains_set, hops_set, yeasts_set, recipe_mapping


def proc():
    gs, hs, ys, mapping = beer_xml()

    with open(Path(processed_path, "hops.json"), "w") as fp:
        json.dump(list(hs), fp)

    with open(Path(processed_path, "yeasts.json"), "w") as fp:
        json.dump(list(ys), fp)

    with open(Path(processed_path, "grains.json"), "w") as fp:
        json.dump(list(gs), fp)

    mapping2 = {}
    for m in mapping.keys():
        gs = list(mapping[m]["grains"])
        hs = list(mapping[m]["hops"])
        ys = list(mapping[m]["yeasts"])
        mapping2[str(m)] = dict(grains=gs, hops=hs, yeasts=ys)

    with open(Path(processed_path, "mapping.json"), "w") as fp:
        json.dump(mapping2, fp)


def new_way():
    try1 = Path(download_path)
    bxmls = try1.iterdir()
    parser = Parser()
    # df = pd.DataFrame()
    rows = []
    # count = 0
    for b in bxmls:
        # count = count+1
        recipes = parser.parse(b)
        grains = [grain.name for grain in recipes[0].fermentables]
        hops = [hop.name for hop in recipes[0].hops]
        yeasts = [yeast.name for yeast in recipes[0].yeasts]
        gw, hw, yw = unique_words(grains=grains, hops=hops, yeasts=yeasts)
        cols = set()
        cols.update(gw)
        cols.update(hw)
        cols.update(yw)

        counts = {col: 1 for col in cols}
        ingr = dict(_grains=gw, _hops=hw, _yeasts=yw)
        ingr.update(counts)
        ingr.update(dict(recipe=str(b)))
        # b_df = pd.DataFrame.from_dict(row,orient="index")
        rows.append(ingr)
        # if count > 10:
        #     return rows
    return rows


def prep_bot():
    bot_prep_path = Path(processed_path, "mapping.json")
    df = pd.read_json(bot_prep_path, orient="index")
    df.rename(
        columns={"grains": "_grains", "hops": "_hops", "yeasts": "_yeasts"},
        inplace=True,
    )

    with open(Path(processed_path, "grains.json")) as fp:
        grains = json.load(fp)
    for grain in grains:
        _grains = df["_grains"].apply(
            lambda x: 1 if grain in x else np.nan  # noqa: B023
        )
        df[grain] = df[grain] + _grains if grain in df.columns else _grains

    with open(Path(processed_path, "hops.json")) as fp:
        hops = json.load(fp)
    for hop in hops:
        _hops = df["_hops"].apply(lambda x: 1 if hop in x else np.nan)  # noqa: B023
        df[hop] = df[hop] + _hops if hop in df.columns else _hops

    with open(Path(processed_path, "yeasts.json")) as fp:
        yeasts = json.load(fp)
    for yeast in yeasts:
        _yeasts = df["_yeasts"].apply(
            lambda x: 1 if yeast in x else np.nan  # noqa: B023
        )
        df[yeast] = df[yeast] + _yeasts if yeast in df.columns else _yeasts

    with open(Path(bot_path, "bot.json"), "w") as fp:
        df.to_json(fp)


def bot_pickle():
    with open(Path(bot_path, "bot.json")) as fp:
        df = pd.read_json(fp)
    path = Path(bot_path, "bot.pickle").absolute()
    df.to_pickle(path)


def oto():
    logger.info("getting all ids")
    bfids = get_brewers_friend_ids()
    logger.info(len(bfids))
    logger.info("downloading recipes")
    download_recipes(bfriendids=bfids)
    logger.info("reading all into beer-xml")
    proc()
    logger.info("proc folder updated with grain/hops/yeast and mapping")
    prep_bot()
    bot_pickle()


def cleanup():  # TODO
    from spellchecker import SpellChecker

    spell = SpellChecker()
    # find those words that may be misspelled
    misspelled = spell.unknown(
        [
            "chocolate",
            "chocolat",
            "choco",
            "choc",
            "chocolademout",
            "chocosimpsons",
            "choclate",
            "blackswaenchocolate",
        ]
    )
    for word in misspelled:
        # Get the one `most likely` answer
        logger.info(spell.correction(word))
        # Get a list of `likely` options
        logger.info(spell.candidates(word))


def bot_new():
    path = bot2_pickle
    df = pd.read_pickle(path)
    df["file"] = df.index.map(
        lambda i: i.replace(
            "/Users/clowjp/workspace/kitchensink/downloads/try1/",
            "/Users/clowjp/github_workspace/mashmaestro/downloads/try1/",
        )
    )
    df["beer_name"] = df["file"].apply(lambda i: bot_to_beer_name(i))
    urls = brew_urls()
    df["beer_urls"] = df["beer_name"].apply(lambda i: urls.get(i))
    df.to_pickle(bot3_pickle)


def brew_urls():
    bfriend_name_url_mapping = {}
    with open(kaggle_csv, errors="replace") as recipes:
        recipes = recipes.readlines()
    spamreader = csv.reader(recipes, delimiter=",")
    next(spamreader)
    for row in spamreader:
        name = row[1]
        url = row[2]  # URL
        bfriend_name_url_mapping[name] = f"https://www.brewersfriend.com{url}"
    return bfriend_name_url_mapping


def bot_to_beer_name(bot_xml_path):
    b = Path(bot_xml_path)  # 8 wired Tall Poppy Clone
    parser = Parser()
    recipes = parser.parse(b)
    return recipes[0].name


if __name__ == "__main__":
    rows = new_way()
    df = pd.DataFrame.from_records(rows, index="recipe")
    # bot_pickle()
    path = Path(bot_path, "bot2.pickle").absolute()
    df.to_pickle(path)
    bot_new()
