# bot.py
import os

import discord
import pandas as pd
from discord import Intents
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv

from mashmaestro.language import make_columns, make_words
from mashmaestro.logger import logger
from mashmaestro.runner import bot_new, must, queries, reduce, top_n

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = Intents(dm_messages=True)
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} has connected to Discord!")


def author_name(ctx: Context):
    return ctx.message.author.name


df = bot_new()
user_df: pd.DataFrame = pd.DataFrame()
user_words: dict[str, set[str]] = dict(
    grains=set(), hops=set(), yeasts=set(), must=set()
)


@bot.command(name="new", aliases=["n"], help="Starts a new MashMaestro session")
async def new(ctx: Context):
    game = discord.Game("Brewing with {}".format(author_name(ctx=ctx)))
    await bot.change_presence(activity=game)

    global user_df, user_words
    user_df = df.copy()
    user_words = dict(grains=set(), hops=set(), yeasts=set(), must=set())

    await ctx.send(f"{author_name(ctx=ctx)} let's brew!")


@bot.command(name="query", aliases=["q"], help="Provide query results for X=1")
async def query(ctx: Context, recipes: int = 1):
    global user_df
    top = top_n(df=user_df, n=recipes)
    recipe_list = top["beer_urls"].values
    recipe_list = list(filter(None, recipe_list))
    recipe_list = ["https://www.brewersfriend.com"] if not recipe_list else recipe_list
    await ctx.send("{}".format("\n---\n".join(recipe_list)))


def all_user_words() -> list[str]:
    global user_words
    all_words = set()
    all_words.update(user_words["grains"])
    all_words.update(user_words["hops"])
    all_words.update(user_words["yeasts"])
    all_words.update(user_words["must"])
    return list(all_words)


@bot.command(name="grain", aliases=["g"], help="Provide a grain or list of grains")
async def grain(ctx: Context, *args):
    global user_df, user_words
    user_words["grains"].update(make_words(words=[args]))
    user_df = queries(all_user_words(), df=user_df)
    await query(ctx, recipes=1)


@bot.command(name="hop", aliases=["h"], help="Provide a hop or list of hops")
async def hop(ctx: Context, *args):
    global user_df, user_words
    user_words["hops"].update(make_words(words=[args]))
    user_df = queries(all_user_words(), df=user_df)
    await query(ctx, recipes=1)


@bot.command(name="yeast", aliases=["y"], help="Provide a yeast or list of yeats")
async def yeast(ctx: Context, *args):
    global user_df, user_words
    user_words["yeasts"].update(make_words(words=args))
    user_df = queries(all_user_words(), df=user_df)
    await query(ctx, recipes=1)


@bot.command(name="brew", aliases=["b"], help="Reduce")
async def brew(ctx: Context):
    global user_df
    user_df = reduce(user_df)
    await query(ctx, recipes=1)


@bot.command(name="must", aliases=["m"], help="recipe must have this ingredient")
async def bmust(ctx: Context, must_txt: str):
    global user_df, user_words
    user_words["must"].update(make_words(words=[must_txt]))
    user_df = must(user_words["must"], df=user_df)
    user_df = queries(all_user_words(), df=user_df)
    await query(ctx, recipes=1)


@bot.command(name="deets", aliases=["d"], help="show details")
async def deets(ctx: Context, recipes: int = 3):
    global user_df, user_words
    df_opt = user_df.copy()
    col_list = make_columns(make_words(words=all_user_words()), df=df)
    dfn = df_opt[["_grains", "_hops", "_yeasts", "Sum"] + col_list]
    dfn.dropna(axis=1, how="all", inplace=True)
    recs = dfn.head(recipes).to_markdown(index=False)
    await ctx.send("```markdown\n{}\n```".format(recs))


@bot.command(name="inventory", aliases=["i"], help="show inventory entered")
async def inventory(ctx: Context):
    global user_words
    logs = [
        f"{key}:\n\t{','.join(values)}" for key, values in user_words.items() if values
    ]
    await ctx.send("{}".format("\n".join(logs)))


@bot.command(name="count", aliases=["c"], help="how many recipes are elliglbe")
async def count(ctx: Context):
    global user_df
    await ctx.send("{}".format(len(user_df.index)))


bot.run(TOKEN)
logger.info("")
