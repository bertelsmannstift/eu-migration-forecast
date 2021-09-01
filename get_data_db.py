import random
import string
import unicodedata as ud  # greek diacritics only
from datetime import datetime
from re import search

import pandas as pd
from googleapiclient.discovery import build
from sqlalchemy import select
from unidecode import unidecode  # to remove diacritics

from db_stuff import db_connector

START_DATE = "2007-01"
END_DATE = "2020-12"
DATA_VERSION = "21-04-22"

db = db_connector()

with db.get_session() as session:
    version = pd.read_sql(
        select(db.Version).filter(
            db.Version.version == DATA_VERSION),
        session.bind)['id'].values[0].item()
    languages = pd.read_sql(select(db.Language), session.bind)
    countries = pd.read_sql(select(db.Country), session.bind)
    keywords = pd.read_sql(
        select(db.Keyword).filter(
            db.Keyword.version_id == version),
        session.bind)
    assignments = pd.read_sql(select(db.Assignment), session.bind)

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


def add_germany(row, germany_word: str) -> str:
    row['keyword'] = " + ".join([x.strip() +
                                 " " +
                                 germany_word for x in row['keyword'].split("+")])
    return row


def rand_str(chars=string.ascii_uppercase + string.digits, N=20):
    return "".join(random.choice(chars) for _ in range(N))


def add_removed_diacritics(row, fcn=unidecode):
    row['keyword'] = " + ".join([s.strip() if s == fcn(s) else s.strip() + " + " + fcn(s)
                                 for s in row['keyword'].split("+")])
    return row


def get_response(term, geo):
    return pd.DataFrame(
        service.getGraph(
            terms=term,
            restrictions_startDate=START_DATE,
            restrictions_endDate=END_DATE,
            restrictions_geo=geo,
        ).execute()["lines"][0]["points"]
    ).assign(**{"country": geo, "term": term})


# keywords = keywords[keywords['without_germany'] == True]
# add "germany"
keywords = keywords.apply(
    lambda row: add_germany(
        row, languages[languages['id'] == row['language_id']]['germany'].values[0])
    if row['without_germany'] == False
    else row,
    axis=1,
)

# # lower case
keywords['keyword'] = keywords['keyword'].str.lower()

# remove diacritics
keywords = keywords.apply(
    lambda row: add_removed_diacritics(row)
    if languages[languages['id'] == row['language_id']]['remove_diacritics'].values[0] == True
    else row,
    axis=1
)

## --------------------------------------------- ##
# Greek diacritics
## --------------------------------------------- ##

# build searchwords
searchwords = pd.merge(
    keywords,
    assignments,
    on='language_id')\
    .assign(count=1).groupby(['country_id', 'version_id', 'keyword_id']).agg(
        {'keyword': lambda x: " + ".join(set(x))}).reset_index()
searchwords.rename(
    columns={
        'keyword': 'searchword'},
    inplace=True)

## --------------------------------------------- ##
# synch searchwords with db to get correct ids
## --------------------------------------------- ##

searchwords = db.clean_df_db_dups(
    searchwords, 'trend.d_searchword', [
        'country_id', 'version_id', 'keyword_id'])

searchwords.to_sql(
    'd_searchword',
    db.engine,
    schema='trend',
    method=db.psql_insert_copy,
    if_exists='append',
    index=False)

with db.get_session() as session:
    searchwords = pd.read_sql(
        select(db.Searchword).filter(
            db.Searchword.version_id == version),
        session.bind)

searchwords = searchwords.merge(
    countries, left_on='country_id', right_on='id')

searchwords['searchword'] = searchwords['searchword'].apply(
    lambda s: s + ' + ' + rand_str()
)

responses = pd.concat([d for d in searchwords.apply(
    lambda row: get_response(row['searchword'], row['short']),
    axis=1,
)], ignore_index=True)


# # korrekte response table bauen
responses = (
    responses.merge(
        searchwords, left_on=['term', 'country'], right_on=['searchword', 'short']
    )
    .drop(columns=['country_x', 'country_y', 'term', 'searchword', 'short', 'keyword_id', 'country_id', 'version_id', 'id_y'])
    .rename(columns={"id_x": "searchword_id", "Keyword": "keyword"})

)
responses.loc[:, 'iteration'] = 1
responses.loc[:, 'date_of_retrieval'] = datetime.now()
responses = responses[['searchword_id', 'iteration',
                       'date', 'value', 'date_of_retrieval']]

responses.to_sql(
    'd_trends',
    db.engine,
    schema='trend',
    method=db.psql_insert_copy,
    if_exists='append',
    index=False)


# # responses zur DB schreiben
