# %%
import pandas as pd
from sqlalchemy import select

from db_stuff import db_connector

KEYWORD_FILE = "data/keywords/keywords-prototype-21-04-22.xlsx"
DATA_VERSION = "21-04-22"

db = db_connector()

df_keywords = pd.read_excel(KEYWORD_FILE)

df_keywords = df_keywords.loc[~df_keywords["KeywordID"].isna()]
df_keywords["KeywordID"] = df_keywords["KeywordID"].astype(int)

# %%
languages = set(df_keywords.columns)
languages.remove('FlagWithoutGermany')
languages.remove('KeywordID')
languages


# %%
def get_language_id(language):
    with db.get_session() as session:
        return pd.read_sql(
            select(db.Language).filter(
                db.Language.short == language),
            session.bind)['id'].values[0].item()


def get_version_id(version):
    with db.get_session() as session:
        return pd.read_sql(
            select(db.Version).filter(
                db.Version.version == version),
            session.bind)['id'].values[0].item()


version_id = get_version_id(DATA_VERSION)

for language in languages:
    if 'keywords' in globals():
        del keywords
    print(language)
    language_id = get_language_id(language)
    keywords = df_keywords[['KeywordID',
                            language, 'FlagWithoutGermany']].copy()
    keywords.loc[:, ('FlagWithoutGermany')] = keywords.apply(
        lambda row: 0 if row.isna()["FlagWithoutGermany"]
        else 1,
        axis=1
    ).astype('bool')
    keywords.loc[:, 'language_id'] = language_id
    keywords.loc[:, 'version_id'] = version_id
    keywords.rename(
        columns={
            'KeywordID': 'keyword_id',
            'FlagWithoutGermany': 'without_germany',
            language: 'keyword',
            'index': 'id'},
        inplace=True)
    keywords = keywords[['keyword_id', 'language_id',
                         'version_id', 'without_germany', 'keyword']]
    keywords.to_sql(
        'l_keyword',
        db.engine,
        schema='trend',
        method=db.psql_insert_copy,
        if_exists='append',
        index=False)
