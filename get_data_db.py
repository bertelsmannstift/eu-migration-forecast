import random
import string
import unicodedata as ud  # greek diacritics only

import pandas as pd
from googleapiclient.discovery import build
from unidecode import unidecode  # to remove diacritics

from db_stuff import db_connector

START_DATE = "2007-01"
END_DATE = "2020-12"

db = db_connector()

languages = pd.DataFrame([x._as_dict() for x in db.get_languages()])
countries = pd.DataFrame([x._as_dict() for x in db.get_countries()])
keywords = pd.DataFrame([x._as_dict() for x in db.get_keywords()])
assignments = pd.DataFrame([x._as_dict()
                           for x in db.get_assignments()])

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

searchwords.to_sql(
    'd_searchword',
    db.engine,
    schema='trend',
    method=db.psql_insert_copy,
    if_exists='append',
    index=False)


# s = df.assign(count=1).groupby(['gb1',
#                                 'gb2']).agg({'count': 'sum',
#                                              'text1': lambda x: ','.join(set(x)),
#                                              'text2': lambda x: ','.join(set(x))}).reset_index()
