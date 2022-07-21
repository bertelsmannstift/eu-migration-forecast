from dataclasses import dataclass, field
from dotenv import load_dotenv, find_dotenv
import os

import random
import string
from sys import api_version
import unicodedata as ud  # greek diacritics only
from datetime import datetime
from tqdm import tqdm

import pandas as pd
from googleapiclient.discovery import build
from pandas.core.frame import DataFrame
from sqlalchemy import select
from unidecode import unidecode  # to remove diacritics

from modules.eumf_db import DBConnector

load_dotenv(find_dotenv())

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(THIS_DIR, "../data/raw/trends/")

@dataclass
class GoogleTrendsConnector:
    server: str = "https://trends.googleapis.com"
    api_version: str = "v1beta"
    # service = field(init=False)

    def __post_init__(self):
        discovery_url_suffix = "/$discovery/rest?version=" + self.api_version
        discovery_url = self.server + discovery_url_suffix

        self.service = build(
            "trends",
            api_version,
            developerKey=os.environ.get("GOOGLE_DEVELOPER_KEY"),
            discoveryServiceUrl=discovery_url,
        )

    def get_response(
        self, term: str, geo: str, start_date: str, end_date: str
    ) -> DataFrame:
        return pd.DataFrame(
            self.service.getGraph(
                terms=term + " + " + rand_str(),
                restrictions_startDate=start_date,
                restrictions_endDate=end_date,
                restrictions_geo=geo,
            ).execute()["lines"][0]["points"]
        ).assign(**{"country": geo, "term": term})


def add_destination(obj, dest_word: str, is_row: bool = True) -> str:
    kw = obj["keyword"] if is_row else obj
    new_expr = " + ".join([x.strip() + " " + dest_word for x in kw.split("+")])
    if is_row:
        obj["keyword"] = new_expr
        return obj
    else:
        return new_expr


def rand_str(chars=string.ascii_uppercase + string.digits, N=20) -> str:
    return "".join(random.choice(chars) for _ in range(N))


def add_removed_diacritics(obj, fcn=unidecode, is_row: bool = True):
    kw = obj["keyword"] if is_row else obj
    new_expr = " + ".join(
        [
            s.strip() if s == fcn(s) else s.strip() + " + " + fcn(s)
            for s in kw.split("+")
        ]
    )
    if is_row:
        obj["keyword"] = new_expr
        return obj
    else:
        return new_expr


def strip_greek_accents(s: str) -> str:
    return (
        ud.normalize("NFD", s)
        .translate({ord("\N{COMBINING ACUTE ACCENT}"): None})
        .strip()
    )


def prepare_searchwords(
    keywords: DataFrame, assignments: DataFrame, languages: DataFrame
) -> DataFrame:
    # keywords = keywords[keywords['without_germany'] == True]
    # add 'germany'
    keywords = keywords.apply(
        lambda row: add_destination(
            row, languages[languages["id"] == row["language_id"]]["germany"].values[0]
        )
        if row["without_germany"] == False
        else row,
        axis=1,
    )

    # # lower case
    keywords["keyword"] = keywords["keyword"].str.lower()

    # remove diacritics
    keywords = keywords.apply(
        lambda row: add_removed_diacritics(row)
        if languages[languages["id"] == row["language_id"]]["remove_diacritics"].values[
            0
        ]
        == True
        else row,
        axis=1,
    ).apply(
        lambda row: add_removed_diacritics(row, fcn=strip_greek_accents)
        if row["language_id"] == languages[languages["short"] == "EL"]["id"].values[0]
        else row,
        axis=1,
    )

    # build searchwords
    searchwords = (
        pd.merge(keywords, assignments, on="language_id")
        .assign(count=1)
        .groupby(["country_id", "version_id", "keyword_id"])
        .agg({"keyword": lambda x: " + ".join(set(x))})
        .reset_index()
    )
    searchwords.rename(columns={"keyword": "searchword"}, inplace=True)
    return searchwords


def sync_searchwords_db(
    db: DBConnector, searchwords: DataFrame, countries: DataFrame, version: int
) -> DataFrame:
    searchwords = db.clean_df_db_dups(
        searchwords, "trend.d_searchword", ["country_id", "version_id", "keyword_id"]
    )

    searchwords.to_sql(
        "d_searchword",
        db.engine,
        schema="trend",
        method=db.psql_insert_copy,
        if_exists="append",
        index=False,
    )

    with db.get_session() as session:
        searchwords = pd.read_sql(
            select(db.Searchword).filter(db.Searchword.version_id == version),
            session.bind,
        )

    searchwords = searchwords.merge(countries, left_on="country_id", right_on="id")

    return searchwords


def get_trends(
    trends: GoogleTrendsConnector,
    searchwords: DataFrame,
    start_date: str,
    stop_date: str,
    verbose: bool = True,
) -> DataFrame:

    response_func = lambda row: trends.get_response(
        row["searchword"], row["short"], start_date, stop_date
    )

    if verbose:
        tqdm.pandas()
        responses = searchwords.progress_apply(response_func, axis=1,)
    else:
        responses = searchwords.apply(response_func, axis=1,)
    responses = pd.concat([d for d in responses], ignore_index=True,)

    return responses


def trends_to_db(
    db: DBConnector, responses: pd.DataFrame, searchwords: pd.DataFrame, iteration: int
):
    responses = (
        responses.merge(
            searchwords, left_on=["term", "country"], right_on=["searchword", "short"],
        )
        .drop(
            columns=[
                "country_x",
                "country_y",
                "term",
                "searchword",
                "short",
                "keyword_id",
                "country_id",
                "version_id",
                "id_y",
            ]
        )
        .rename(
            columns={
                "id_x": "searchword_id",
                "Keyword": "keyword",
                "date": "date_of_value",
            }
        )
    )

    responses.loc[:, "iteration"] = iteration
    responses.loc[:, "date_of_retrieval"] = datetime.now()
    responses = responses[
        ["searchword_id", "iteration", "value", "date_of_value", "date_of_retrieval",]
    ]

    responses.to_sql(
        "d_trends",
        db.engine,
        schema="trend",
        method=db.psql_insert_copy,
        if_exists="append",
        index=False,
    )


def trends_to_csv(
    responses: pd.DataFrame,
    searchwords: pd.DataFrame,
    country: str,
    data_version: str,
    iteration: int,
):
    responses = (
        responses.merge(
            searchwords[["searchword", "short", "keyword_id"]],
            left_on=["term", "country"],
            right_on=["searchword", "short"],
        ).rename(columns={"term": "keyword"})
    )[["value", "date", "keyword_id", "keyword"]]

    responses.to_csv(get_trends_output_filename(country, data_version, iteration))


def get_trends_output_filename(country: str, data_version: str, iteration: int) -> str:
    directory = os.path.join(DATA_DIR, data_version)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(directory, f"data_{country}_{iteration}.csv")
