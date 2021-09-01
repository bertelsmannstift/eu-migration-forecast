import csv
from collections.abc import Iterable, Iterator
from io import StringIO
from typing import List

import pandas as pd
from sqlalchemy import (Boolean, Column, Integer, MetaData, String, Table,
                        create_engine, inspect, select)
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true

Base = declarative_base()


class db_connector:

    class Version(Base):
        __tablename__ = 'l_version'
        __table_args__ = {"schema": "trend"}

        id = Column(Integer, primary_key=true)
        version = Column(String)

    class Language(Base):
        __tablename__ = 'l_language'
        __table_args__ = {"schema": "trend"}

        id = Column(Integer, primary_key=true)
        short = Column(String)
        remove_diacritics = Column(Boolean)
        germany = Column(String)

    class Keyword(Base):
        __tablename__ = 'l_keyword'
        __table_args__ = {"schema": "trend"}

        id = Column(Integer, primary_key=true)
        keyword_id = Column(Integer)
        language_id = Column(Integer)
        version_id = Column(Integer)
        without_germany = Column(Boolean)
        keyword = Column(String)

    class Country(Base):
        __tablename__ = 'l_country'
        __table_args__ = {"schema": "trend"}

        id = Column(Integer, primary_key=true)
        short = Column(String)
        country = Column(String)

    class Assignment(Base):
        __tablename__ = 'a_country_language'
        __table_args__ = {"schema": "trend"}

        id = Column(Integer, primary_key=true)
        country_id = Column(Integer)
        language_id = Column(Integer)

    class Searchword(Base):
        __tablename__ = 'd_searchword'
        __table_args__ = {'schema': 'trend'}

        id = Column(Integer, primary_key=true)
        country_id = Column(Integer)
        version_id = Column(Integer)
        keyword_id = Column(Integer)
        searchword = Column(String)

    def __init__(self) -> None:
        self.connection_string = URL.create(
            drivername='postgresql+psycopg2',
            username='postgres',
            password='postgres',
            host='localhost',
            port='5432',
            database='postgres')
        self.engine = create_engine(
            self.connection_string)
        self.metadata = MetaData(bind=None)

    def get_language_id(self, language):

        table = Table(
            'l_language',
            self.metadata,
            schema='trend',
            autoload=True,
            autoload_with=self.engine
        )

        stmt = select([table.columns.id]).where(
            table.columns.short == language)
        with Session(self.engine) as session:
            return session.execute(stmt).first()

    def get_session(self) -> Session:
        return Session(self.engine)

    def psql_insert_copy(self, table, conn, keys, data_iter):
        # gets a DBAPI connection that can provide a cursor
        dbapi_conn = conn.connection
        with dbapi_conn.cursor() as cur:
            s_buf = StringIO()
            writer = csv.writer(s_buf)
            writer.writerows(data_iter)
            s_buf.seek(0)

            columns = ', '.join('"{}"'.format(k) for k in keys)
            if table.schema:
                table_name = '{}.{}'.format(
                    table.schema, table.name)
            else:
                table_name = table.name

            sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
                table_name, columns)
            cur.copy_expert(sql=sql, file=s_buf)

    def clean_df_db_dups(self, df, tablename, dup_cols=[],
                         filter_continuous_col=None, filter_categorical_col=None):
        """
        Remove rows from a dataframe that already exist in a database
        Required:
            df : dataframe to remove duplicate rows from
            engine: SQLAlchemy engine object
            tablename: tablename to check duplicates in
            dup_cols: list or tuple of column names to check for duplicate row values
        Optional:
            filter_continuous_col: the name of the continuous data column for BETWEEEN min/max filter
                                can be either a datetime, int, or float data type
                                useful for restricting the database table size to check
            filter_categorical_col : the name of the categorical data column for Where = value check
                                    Creates an "IN ()" check on the unique values in this column
        Returns
            Unique list of values from dataframe compared to database table
        """
        args = 'SELECT %s FROM %s' % (
            ', '.join(['"{0}"'.format(col) for col in dup_cols]), tablename)
        args_contin_filter, args_cat_filter = None, None
        if filter_continuous_col is not None:
            if df[filter_continuous_col].dtype == 'datetime64[ns]':
                args_contin_filter = """ "%s" BETWEEN Convert(datetime, '%s')
                                            AND Convert(datetime, '%s')""" % (filter_continuous_col,
                                                                              df[filter_continuous_col].min(), df[filter_continuous_col].max())

        if filter_categorical_col is not None:
            args_cat_filter = ' "%s" in(%s)' % (filter_categorical_col,
                                                ', '.join(["'{0}'".format(value) for value in df[filter_categorical_col].unique()]))

        if args_contin_filter and args_cat_filter:
            args += ' Where ' + args_contin_filter + ' AND' + args_cat_filter
        elif args_contin_filter:
            args += ' Where ' + args_contin_filter
        elif args_cat_filter:
            args += ' Where ' + args_cat_filter

        df.drop_duplicates(dup_cols, keep='last', inplace=True)
        df = pd.merge(
            df,
            pd.read_sql(
                args,
                self.engine),
            how='left',
            on=dup_cols,
            indicator=True)
        df = df[df['_merge'] == 'left_only']
        df.drop(['_merge'], axis=1, inplace=True)
        return df
