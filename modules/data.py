#%%

from collections.abc import Callable
from collections.abc import Iterable
from typing import Optional, Union, Any
import json
import pandas as pd
import os

# from pandas.core.frame import DataFrame

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_FILE_MIGRATION = (
    THIS_DIR + "/../data/migration_rates/migration_rate_processed.csv"
)
DEFAULT_FILE_COUNTRIES = THIS_DIR + "/../data/migration_rates/countries.json"
DEFAULT_DIR_TRENDS = THIS_DIR + "/../data/processed_data"
DEFAULT_PREFIX_TRENDS = "processed_"
DEFAULT_FILE_LANG_ASSIGNMENT = (
    THIS_DIR + "/../data/keywords/assignment_language_country.json"
)


def get_countries(country_file: str = DEFAULT_FILE_COUNTRIES):
    with open(country_file) as buf:
        countries = list(json.load(buf).keys())
    return countries


def load_migration_rates_from_csv(
    data_file: str = DEFAULT_FILE_MIGRATION, country_file: str = DEFAULT_FILE_COUNTRIES,
) -> dict[str, pd.Series]:

    countries = get_countries(country_file)

    data = pd.read_csv(data_file, index_col=0, parse_dates=["date"],)
    data.set_index("date", inplace=True)
    data["value"] = pd.to_numeric(data["value"], errors="coerce").fillna(0.0)

    # fill missing data with mean
    # for c in countries:
    #     df_all.loc[df_all["country"] == c, "value"].fillna(
    #         df_all.loc[df_all["country"] == c].mean(), inplace=True
    #     )

    # data = {c: df_all[df_all.country == c].value for c in countries}

    return data.pivot(columns="country")


def get_trends_input_file(
    country: str,
    data_version: str,
    data_dir: str = DEFAULT_DIR_TRENDS,
    data_file_prefix: str = DEFAULT_PREFIX_TRENDS,
) -> str:

    directory = os.path.join(data_dir, data_version)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(directory, f"{data_file_prefix}{country}.csv")


def load_trends_from_csv(
    data_version: str = "21-04-22",
    country_file: str = DEFAULT_FILE_COUNTRIES,
    **kwargs,
) -> tuple[dict[pd.DataFrame], list[str]]:

    countries = get_countries(country_file)

    data = {
        c: pd.read_csv(
            get_trends_input_file(c, data_version, **kwargs),
            header=[0, 1],
            index_col=0,
            parse_dates=[0],
        )["mean"]
        for c in countries
    }

    # return data
    return (
        pd.concat(data, axis=1)
        .swaplevel(axis="columns")
        .sort_index(axis="columns", level=0)
    )


def create_lags(
    df: pd.DataFrame,
    lags: Union[int, Iterable[int]],
    columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    if columns is None:
        columns = df.columns
    if not isinstance(lags, Iterable):
        lags = [lags]
    df_list = []
    for l in lags:
        df_list.append(
            df[columns].shift(l).rename(columns=lambda x: x + f"_{l}", level=0)
        )
    return pd.concat(df_list, axis="columns")


def stack(X: pd.DataFrame, y: pd.DataFrame, add_column: bool = True):
    if add_column:
        X_stacked = X.stack().reset_index(level=1)
    else:
        X_stacked = X.stack().droplevel(level=1)
    y_stacked = y.stack().droplevel(level=1)
    return X_stacked, y_stacked

