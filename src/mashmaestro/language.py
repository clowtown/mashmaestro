def treat(word):
    import re
    import string

    str_word = str(word).lower()
    ascii_word = str_word.encode("ascii", "ignore").decode()
    no_punct = re.sub("[%s]" % re.escape(string.punctuation), " ", ascii_word)
    words = no_punct.split()  # 2-row
    return words


def word_set(words: list[str]):
    wordset = set()
    for x in words:
        xs = treat(word=x)
        wordset.update(xs)
    return wordset


def unique_words(grains, hops, yeasts):
    gwords = word_set(words=grains)

    hwords = word_set(words=hops)

    ywords = word_set(words=yeasts)
    return gwords, hwords, ywords


def make_words(words: list[str]) -> list[str]:
    col_list = words
    col_list = [treat(col) for col in col_list]
    col_list = [item for col in col_list for item in col]
    return col_list


def make_columns(words: list[str], df) -> list[str]:
    col_list = set(words).intersection(df.columns)
    col_list = list(col_list)
    return col_list
