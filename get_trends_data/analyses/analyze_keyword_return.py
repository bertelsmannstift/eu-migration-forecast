#%%
#
import os
import pandas as pd
import numpy as np
from apiclient.discovery import build
import json
from IPython.display import display

from typing import Iterable

pd.set_option("display.max_rows", 200)


#%%
# connect to google trends api

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

start_date = "2004-01"
end_date = "2020-12"


#%%
# retrieve keywords

df_keywords = pd.read_excel(
    "../keywords/MigFor-Schlagwörter-Alle Sprachen22.02.21.xlsx"
)

df_keywords = df_keywords.loc[~df_keywords["KeywordID"].isna()]
df_keywords["KeywordID"] = df_keywords["KeywordID"].astype(int)

# remove nationality groups, try manually
df_keywords = df_keywords.loc[df_keywords["KeywordID"] != 1]

with open("../keywords/germany_language_keywords.json") as f:
    germany_language_keywords = json.load(f)


def add_germany(string: str, germany_word: str) -> str:
    return " + ".join([x + " " + germany_word for x in string.split("+")])


# exclude certain keywords from adding "germany"
sub_df_w_germany = df_keywords[df_keywords["FlagWithoutGermany"].isna()]
sub_df_wo_germany = df_keywords[~df_keywords["FlagWithoutGermany"].isna()]

for col in df_keywords.columns:
    if col in germany_language_keywords.keys():
        sub_df_w_germany[col] = sub_df_w_germany[col].apply(
            add_germany, args=[germany_language_keywords[col]]
        )

df_keywords = pd.concat([sub_df_w_germany, sub_df_wo_germany])
df_keywords

df_keywords


#%%
# retrieve countries and languages

with open("../keywords/assignment_language_country.json") as f:
    assignment_language_country = json.load(f)

countries = assignment_language_country.keys()


def get_output_file(country: str) -> str:
    return f"../data/data_{country}.csv"


#%%
# get responses for each country


def get_response(term, geo):
    print(term)
    return pd.DataFrame(
        service.getGraph(
            terms=term,
            restrictions_startDate=start_date,
            restrictions_endDate=end_date,
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

    # display(df_keywords_country)

    df_responses = pd.concat(
        [get_response(k, country) for k in df_keywords_country["Keyword"]]
    )

    df_responses = df_responses.merge(
        df_keywords_country, how="left", left_on="term", right_on="Keyword"
    ).drop(columns=["country", "term"])

    # display(df_responses)

    df_responses.to_csv(get_output_file(country))

#%%
# discover missing responses for each country


def get_missing_file(country: str) -> str:
    return f"../data/missing_{country}.xlsx"


for country in countries:

    try:
        df_responses = pd.read_csv(get_output_file(country), index_col=0)
    except:
        continue

    if os.path.isfile(get_missing_file(country)):
        continue

    df_missing = (
        df_responses[["value", "KeywordID", "Keyword"]]
        .groupby("KeywordID")
        .agg("max")
        .replace([100, 0], ["true", "false"])
        .rename(columns={"value": "Success"})
    ).sort_values("KeywordID")

    df_missing.to_excel(get_missing_file(country))
    display(df_missing)
# df_missing.to_csv("data/missing_EN_IE.csv")

# %%
# aggregate missings

df_missings = []

for country in countries:

    try:
        df_missing = pd.read_excel(get_missing_file(country), index_col=[0, 1])
    except:
        continue

    df_missing["Country"] = country
    df_missings.append(df_missing)

df_missing_all = (
    pd.concat(df_missings)
    .drop(columns="Keyword")
    .reset_index()
    .pivot_table(index="KeywordID", columns="Country", values="Success")
    .reindex(countries, axis="columns")
)

display(df_missing_all)

df_missing_all.to_excel(f"../data/missing_all.xlsx")


# %%
