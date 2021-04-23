#%%
#
import os
import pandas as pd
import numpy as np
import sqlite3
from apiclient.discovery import build
import json
from IPython.display import display
import random
import string

from unidecode import unidecode  # to remove diacritics
import unicodedata as ud  # greek diacritics only

from typing import Iterable

START_DATE = "2007-01"
END_DATE = "2020-12"

KEYWORD_FILE = "keywords/keywords-prototype-21-04-22.xlsx"
LANGUAGE_ASSIGNMENT_FILE = "keywords/assignment_language_country.json"
GERMANY_TRANSLATION_FILE = "keywords/germany_language_keywords.json"

DATA_VERSION = "21-04-22"

# increase iteration to draw more data for averaging
ITERATION = 1


def get_output_file(country: str) -> str:
    directory = f"raw_data/{DATA_VERSION}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(directory, f"data_{country}_{ITERATION}.csv")


# google trends API connection

SERVER = "https://trends.googleapis.com"

API_VERSION = "v1beta"
DISCOVERY_URL_SUFFIX = "/$discovery/rest?version=" + API_VERSION
DISCOVERY_URL = SERVER + DISCOVERY_URL_SUFFIX

service = build(
    "trends",
    "v1beta",
    developerKey="AIzaSyANmyabv5zka2cg0hj07BRiJPMgH6lxM4A",
    discoveryServiceUrl=DISCOVERY_URL,
)

df_keywords = pd.read_excel(KEYWORD_FILE)

df_keywords = df_keywords.loc[~df_keywords["KeywordID"].isna()]
df_keywords["KeywordID"] = df_keywords["KeywordID"].astype(int)

with open(GERMANY_TRANSLATION_FILE) as f:
    germany_language_keywords = json.load(f)


def add_germany(string: str, germany_word: str) -> str:
    return " + ".join([x + " " + germany_word for x in string.split("+")])


def rand_str(chars=string.ascii_uppercase + string.digits, N=10):
    return "".join(random.choice(chars) for _ in range(N))


def add_removed_diacritics(keyword, fcn=unidecode):
    kw_list = [s if s == fcn(s) else s + " + " + fcn(s) for s in keyword.split("+")]
    return "+".join(kw_list)


languages_dia = ["PL", "CS", "SK", "FR", "EL", "HR", "IT", "LV", "LI", "PT", "ES"]

for col in germany_language_keywords.keys():

    # add "germany"
    df_keywords[col] = df_keywords.apply(
        lambda row: add_germany(row[col], germany_language_keywords[col])
        if row.isna()["FlagWithoutGermany"]
        else row[col],
        axis=1,
    )

    # lower case
    df_keywords[col] = df_keywords[col].str.lower()

    # remove diacritics
    if col in languages_dia:
        df_keywords[col] = df_keywords[col].apply(add_removed_diacritics)

    # add random string to shuffle Google Trends samples
    df_keywords[col] = df_keywords[col].apply(lambda s: str(s) + " + " + rand_str())

#%%
# special case: greek diacritics
strip_greek_accents = lambda s: ud.normalize("NFD", s).translate(
    {ord("\N{COMBINING ACUTE ACCENT}"): None}
)

df_keywords["EL"] = df_keywords["EL"].apply(
    add_removed_diacritics, fcn=strip_greek_accents
)

# retrieve countries and languages

with open(LANGUAGE_ASSIGNMENT_FILE) as f:
    assignment_language_country = json.load(f)

countries = assignment_language_country.keys()

# get responses for each country


def get_response(term, geo):
    return pd.DataFrame(
        service.getGraph(
            terms=term,
            restrictions_startDate=START_DATE,
            restrictions_endDate=END_DATE,
            restrictions_geo=geo,
        ).execute()["lines"][0]["points"]
    ).assign(**{"country": geo, "term": term})


for country in countries:

    if os.path.isfile(get_output_file(country)):
        continue

    print("\n" + country + "\n")

    df_keywords_country = df_keywords[
        ["KeywordID"] + assignment_language_country[country]
    ]

    df_keywords_country = pd.melt(
        df_keywords_country,
        id_vars="KeywordID",
        var_name="Language",
        value_name="Keyword",
    )

    df_keywords_country = (
        df_keywords_country.groupby("KeywordID")
        .agg(" + ".join)
        .drop(columns="Language")
        .reset_index()
    )

    df_responses = pd.concat(
        [get_response(k, country) for k in df_keywords_country["Keyword"]]
    )

    df_responses = (
        df_responses.merge(
            df_keywords_country, how="left", left_on="term", right_on="Keyword"
        )
        .drop(columns=["country", "term"])
        .rename(columns={"KeywordID": "keyword_id", "Keyword": "keyword"})
    )

    df_responses.to_csv(get_output_file(country))


# %%
