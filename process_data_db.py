import logging

import pandas as pd
from sqlalchemy import func, select

from modules.eumf_db import DBConnector

logger = logging.getLogger(__name__)

DB = DBConnector()

logger.info('Get data from DB')
with DB.get_session() as session:
    trends = pd.read_sql(
        select(
            DB.Trend.searchword_id,
            DB.Trend.date_of_value,
            func.avg(DB.Trend.value).label('mean'),
            func.stddev(DB.Trend.value).label('stddev'),
            (func.stddev(DB.Trend.value) /
             func.sqrt(func.count(1))).label('sem')
        ).group_by(
            DB.Trend.searchword_id,
            DB.Trend.date_of_value),
        session.bind)

logger.info('Write data to DB')
trends.to_sql(
    'trends',
    DB.engine,
    schema='silver',
    method=DB.psql_insert_copy,
    if_exists='replace',
    index=False)
