""" Data import and basic preprocessing/cleaning """

# %%

from collections.abc import Callable
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Optional, Union, Any
from sklearn import impute
import json
import numpy as np
import pandas as pd
import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

DEFAULT_FILE_REGISTRATIONS = os.path.join(
    THIS_DIR, "../data/processed/registrations/registrations_processed.csv"
)
DEFAULT_FILE_COUNTRIES = os.path.join(
    THIS_DIR, "../data/config/country_names_registrations.json"
)
DEFAULT_DIR_TRENDS = os.path.join(THIS_DIR, "../data/processed/trends")
DEFAULT_PREFIX_TRENDS = "processed_"
DEFAULT_FILE_LANG_ASSIGNMENT = os.path.join(
    THIS_DIR, "../data/config/assignment_language_country.json"
)
DEFAULT_FILE_COUNTRYNAMES_EUROSTAT = os.path.join(
    THIS_DIR, "../data/config/country_names_eurostat.json"
)
DEFAULT_FILE_GDP = os.path.join(THIS_DIR, "../data/raw/eurostat/GDP_pc_quart.xls")
DEFAULT_FILE_UNEMPL = os.path.join(
    THIS_DIR, "../data/raw/eurostat/Unemployment_Rate_Quart.xlsx"
)


def get_countries(country_file: str = DEFAULT_FILE_COUNTRIES):
    with open(country_file) as buf:
        countries = list(json.load(buf).keys())
    return countries


def load_registrations_from_csv(
    data_file: str = DEFAULT_FILE_REGISTRATIONS,
    impute_missing: bool = False,
    imputer_n_neighbors: int = 3,
    countries: Optional[Iterable[str]] = None,
) -> dict[str, pd.Series]:
    # countries = get_countries(country_file)

    data = pd.read_csv(
        data_file,
        index_col=0,
        parse_dates=["date"],
    )
    data.set_index("date", inplace=True)
    data["value"] = pd.to_numeric(data["value"], errors="coerce")

    if countries is not None:
        data = data[data["country"].isin(countries)]

    data = data.pivot(columns="country")

    if impute_missing:
        imputer = impute.KNNImputer(n_neighbors=imputer_n_neighbors)
        imputed = imputer.fit_transform(data.to_numpy())
        data = pd.DataFrame(imputed, index=data.index, columns=data.columns)

    return data


def get_processed_trends_filename(
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
    countries: Optional[Iterable[str]] = None,
    default_country_file: str = DEFAULT_FILE_COUNTRIES,
    **kwargs,
) -> tuple[dict[pd.DataFrame], list[str]]:
    if countries is None:
        countries = get_countries(default_country_file)

    data = {
        c: pd.read_csv(
            get_processed_trends_filename(c, data_version, **kwargs),
            header=[0, 1],
            index_col=0,
            parse_dates=[0],
        )["mean"]
        for c in countries
    }

    return (
        pd.concat(data, axis=1)
        .swaplevel(axis="columns")
        .sort_index(axis="columns", level=0)
    )


def create_lags(
    df: pd.DataFrame,
    lags: Iterable[int],
    columns: Optional[Iterable[str]] = None,
    alternate_lags: dict[str, Iterable[int]] = {},
) -> pd.DataFrame:
    if columns is None:
        columns = df.columns
    df_list = []

    for c in columns:
        if c in alternate_lags.keys():
            lags_tmp = alternate_lags[c]
        else:
            lags_tmp = lags

        for l in lags_tmp:
            df_list.append(
                df[[c]].shift(l).rename(columns=lambda x: x + f"_{l}", level=0)
            )

    return pd.concat(df_list, axis="columns")


@dataclass
class Labeled:
    x: pd.DataFrame
    y: Union[pd.DataFrame, pd.Series]

    def __init__(self, x, y):
        assert np.all(x.index == y.index)
        self.x = x
        self.y = y
        self.index = x.index

    def __getitem__(self, key):
        return Labeled(self.x[key], self.y[key])

    def apply(self, func):
        return Labeled(func(self.x), func(self.y))

    def copy(self):
        return Labeled(self.x, self.y)


def stack_labeled(
    data: Labeled,
    extra_column: bool = True,
    extra_column_name: str = "country",
    pooled: bool = True,
):
    stacked = data.apply(lambda df: df.stack())
    if not pooled:
        df_tmp = stacked.x.copy()
        tmp_dfs = []
        countries = stacked.x.index.get_level_values(1).unique().to_list()
        for col in stacked.x.columns:
            if col != "country":
                df_tmp = stacked.x.copy()
                for c in countries:
                    df_tmp[col + "_" + c] = df_tmp.loc[
                        df_tmp.index.get_level_values(1) == c, col
                    ]
                df_tmp = df_tmp.drop(columns=stacked.x.columns)
                tmp_dfs.append(df_tmp)
        stacked.x = pd.concat(tmp_dfs, axis=1).fillna(0.0)
    if extra_column:
        new_col_dict = {extra_column_name: stacked.x.index.get_level_values(1)}
        stacked.x = stacked.x.assign(**new_col_dict)

    return stacked


def discretize_labeled(
    data: Labeled,
    bins: Iterable[float],
    classes: Iterable,
):
    data_tmp = data.copy()
    data_tmp.y = pd.cut(data_tmp.y, bins, labels=classes)
    return data_tmp


def stack(
    X: pd.DataFrame,
    y: pd.DataFrame,
    extra_column: bool = True,
    extra_column_name="country",
):
    y_stacked = y.stack()
    X_stacked = X.stack()
    if extra_column:
        new_col_dict = {extra_column_name: X_stacked.index.get_level_values(1)}
        X_stacked = X_stacked.assign(**new_col_dict)
        # X_stacked = X_stacked.assign(country=X_stacked.index.get_level_values(1))
    return X_stacked, y_stacked


def read_gdp(
    filename: str = DEFAULT_FILE_GDP,
    countries: Optional[Iterable[str]] = None,
    country_name_file: str = DEFAULT_FILE_COUNTRYNAMES_EUROSTAT,
    skiprows: int = 10,
    nrows: int = 38,
) -> pd.DataFrame:
    with open(country_name_file) as f:
        country_names = json.load(f)

    df = pd.read_excel(filename, skiprows=skiprows, nrows=nrows)

    country_names_inv = {v: k for k, v in country_names.items()}

    df = (
        df[df["GEO/TIME"].isin(country_names.values())]
        .replace(country_names_inv)
        .set_index("GEO/TIME")
        .transpose()
        .stack()
        .reset_index(level=[1])
        .rename(columns={0: "gdp", "GEO/TIME": "country"})
        .pivot(columns="country")
    )

    # add missing countries as zeroes
    for c in country_names.keys():
        if c not in df.columns.get_level_values(1):
            df["gdp", c] = np.zeros(len(df))

    df.index = pd.to_datetime(df.index)
    df = df.resample("3M", closed="left").mean()

    if countries is not None:
        df = df.loc[:, (slice(None), countries)]

    return df


def read_unempl(
    filename: str = DEFAULT_FILE_UNEMPL,
    countries: Optional[Iterable[str]] = None,
    country_name_file: str = DEFAULT_FILE_COUNTRYNAMES_EUROSTAT,
    skiprows: int = 10,
    nrows: int = 29,
) -> pd.DataFrame:
    with open(country_name_file) as f:
        country_names = json.load(f)

    df = pd.read_excel(filename, skiprows=skiprows, nrows=nrows, sheet_name="Sheet 1")

    country_names_inv = {v: k for k, v in country_names.items()}

    df = (
        df.drop(columns=df.filter(like="Unnamed"), index=0)
        .loc[df["TIME"].isin(country_names.values())]
        .replace(country_names_inv)
        .set_index("TIME")
        .transpose()
        .stack()
        .reset_index(level=[1])
        .rename(columns={0: "unempl", "TIME": "country"})
        .replace({":": np.nan})
        .pivot(columns="country")
    )

    # add missing countries as zeroes
    for c in country_names.keys():
        if c not in df.columns.get_level_values(1):
            df["unempl", c] = np.zeros(len(df))

    df.index = pd.to_datetime(df.index)
    df = df.resample("3M", closed="left").mean()

    if countries is not None:
        df = df.loc[:, (slice(None), countries)]

    return df


def combine_countries(
    panel: pd.DataFrame,
    combinations: list[list[str]],
    average: bool = False,
) -> pd.DataFrame:
    panel_swap = panel.swaplevel(0, 1, axis=1)

    for comb in combinations[0:]:
        normalization = len(comb) if average else 1.0
        panel_avg = sum([panel_swap[c] for c in comb]) / normalization
        panel_comb = pd.concat({"+".join(comb): panel_avg}, axis=1)
        panel_swap = panel_swap.join(panel_comb).drop(columns=comb, level=0)

    panel_swap.sort_index(axis=1, level=1, inplace=True)
    panel_combined = panel_swap.swaplevel(0, 1, axis=1)

    return panel_combined
