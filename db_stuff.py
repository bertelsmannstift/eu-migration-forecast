import csv
from collections.abc import Iterable, Iterator
from io import StringIO
from typing import List

from sqlalchemy import (Boolean, Column, Integer, MetaData, String, Table,
                        create_engine, inspect, select)
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true


@as_declarative()
class Base:
    def _as_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


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


class db_connector:

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

    def get_version_id(self, version):
        table = Table(
            'l_version',
            self.metadata,
            schema='trend',
            autoload=True,
            autoload_with=self.engine
        )

        stmt = select([table.columns.id]).where(
            table.columns.version == version)
        with Session(self.engine) as session:
            return session.execute(stmt).first()

    def get_languages(self) -> Iterable[Language]:
        with Session(self.engine) as session:
            return session.query(Language)

    def get_keywords(self) -> Iterable[Keyword]:
        with Session(self.engine) as session:
            return session.query(Keyword)

    def get_countries(self) -> Iterable[Country]:
        with Session(self.engine) as session:
            return session.query(Country)

    def get_assignments(self) -> Iterable[Assignment]:
        with Session(self.engine) as session:
            return session.query(Assignment)

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
