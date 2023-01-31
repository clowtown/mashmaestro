import pandas as pd

from mashmaestro.language import make_columns, make_words
from mashmaestro.paths import bot3_pickle


def query(word: str, df):
    return queries([word], df=df)


def queries(words: list[str], df):
    col_list = make_columns(make_words(words=words), df=df)
    # df.sort_values(by=col_list, inplace=True, ascending=False)
    df["Sum"] = df["Sum"] + df[col_list].sum(axis=1)
    df.sort_values(by=["Sum"], inplace=True, ascending=False)
    return df


def reduce(df):
    # col_list = make_columns(make_words(words=words), df=df)
    # df['Sum'] = df[col_list].sum(axis=1)
    df_opt = df[df["Sum"].apply(lambda s: s > 0)]
    return df_opt


def must(words, df):
    col_list = make_columns(make_words(words=words), df=df)
    df_opt = df.copy()
    for col in col_list:
        df_opt = df_opt[df_opt[col].apply(lambda s: s > 0)]
    return df_opt


def bot_new():
    path = bot3_pickle
    df = pd.read_pickle(path)
    df["Sum"] = 0
    return df


def top_n(df: pd.DataFrame, n) -> pd.DataFrame:
    return df.head(n)
