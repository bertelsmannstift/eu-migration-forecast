import logging
import logging.config

import pandas as pd
from sqlalchemy import select

from modules.eumf_db import DBConnector
from modules.eumf_google_trends import (
    GoogleTrendsConnector,
    get_trends,
    prepare_searchwords,
    sync_searchwords_db,
    trends_to_db,
)

logging.config.fileConfig("logging.conf")

START_DATE = "2007-01"
END_DATE = "2020-12"
DATA_VERSION = "21-04-22"
START_ITERATION = 0
MAX_ITERATION = 10

DB = DBConnector()

TRENDS = GoogleTrendsConnector()


def main():
    logger.info("Get Data...")
    with DB.get_session() as session:
        version = (
            pd.read_sql(
                select(DB.Version).filter(DB.Version.version == DATA_VERSION),
                session.bind,
            )["id"]
            .values[0]
            .item()
        )
        languages = pd.read_sql(select(DB.Language), session.bind)
        countries = pd.read_sql(select(DB.Country), session.bind)
        keywords = pd.read_sql(
            select(DB.Keyword).filter(DB.Keyword.version_id == version), session.bind
        )
        assignments = pd.read_sql(select(DB.Assignment), session.bind)

    logger.info("Prepare Searchwords...")
    searchwords = prepare_searchwords(keywords, assignments, languages)

    logger.info("Sync Searchwords...")
    searchwords = sync_searchwords_db(DB, searchwords, countries, version)

    logger.info("Get Trends...")
    for iteration in range(START_ITERATION, MAX_ITERATION):
        logger.info("Iteration %d", iteration)
        responses = get_trends(TRENDS, searchwords, START_DATE, END_DATE)
        trends_to_db(DB, responses, searchwords, iteration)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Start")
    main()
    logger.info("Finish")
