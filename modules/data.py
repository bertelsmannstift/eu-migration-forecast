#%%

from collections.abc import Callable
from collections.abc import Iterable
from typing import Optional
import json
import pandas as pd
import os

from pandas.core.frame import DataFrame

this_dir = os.path.dirname(os.path.realpath(__file__))


class Dataset:
    def __init__(self, y: dict[str, pd.Series], x: dict[str, pd.DataFrame]):
        self.y = y
        self.x = x
        assert y.keys() == x.keys()
        self.countries = y.keys()
        # TODO: copule of assertions

    def resample(self, freq):
        x_new = {k: df.resample(freq).mean() for k, df in self.x.items()}
        y_new = {k: df.resample(freq).mean() for k, df in self.y.items()}
        return Dataset(y_new, x_new)

    def create_panel(
        self,
        x_lags: Iterable[int] = [1],
        y_lags: Iterable[int] = [1],
        t_min: str = "2010-12-31",
        t_max: str = "2019-12-31",
        add_month_dummies: bool = True,
        wide: bool = False,
    ):
        tmp_dfs = []

        for c in self.countries:
            tmp_df = self.y[c].rename("y").to_frame().assign(country=c)
            if add_month_dummies:
                tmp_df = tmp_df.assign(month=self.y[c].index.month.astype(str))
            for l in y_lags:
                tmp_l = self.y[c].shift(l).rename(f"y_{l}")
                tmp_df = pd.concat([tmp_df, tmp_l], axis=1)
            for l in x_lags:
                tmp_l = self.x[c].shift(l).rename(columns=lambda x: x + f"_{l}")
                tmp_df = pd.concat([tmp_df, tmp_l], axis=1)
            tmp_dfs.append(tmp_df)

        panel = pd.concat(tmp_dfs).sort_index()[t_min:t_max]
        if wide:
            panel = panel.pivot(columns="country")
        return panel


def load_migration_rates_from_csv(
    source_file: str = this_dir + "/../migration_rates/migration_rate_processed.csv",
    country_file: str = this_dir + "/../migration_rates/countries.json",
) -> dict[str, pd.Series]:

    with open(country_file) as buf:
        countries = list(json.load(buf).keys())

    df_all = pd.read_csv(source_file, index_col=0, parse_dates=["date"],)
    df_all.set_index("date", inplace=True)
    df_all["value"] = pd.to_numeric(df_all["value"], errors="coerce")

    for c in countries:
        df_all.loc[df_all["country"] == c, "value"].fillna(
            df_all.loc[df_all["country"] == c].mean(), inplace=True
        )  # fill missing data with mean

    data = {c: df_all[df_all.country == c].value for c in countries}

    return data


def get_trends_input_file(
    country: str,
    data_version: str,
    data_dir: str = this_dir + "/../processed_data",
    data_file_prefix: str = "processed_",
) -> str:

    directory = os.path.join(data_dir, data_version)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(directory, f"{data_file_prefix}{country}.csv")


def load_trends_from_csv(
    data_version: str = "21-04-22",
    lang_assignment_file: str = this_dir
    + "/../keywords/assignment_language_country.json",
    country_file: str = this_dir + "/../migration_rates/countries.json",
    **kwargs,
) -> tuple[dict[pd.DataFrame], list[str]]:

    with open(country_file) as buf:
        countries = list(json.load(buf).keys())

    with open(lang_assignment_file) as f:
        assignment_language_country = json.load(f)

    data = {
        c: pd.read_csv(
            get_trends_input_file(c, data_version, **kwargs),
            header=[0, 1],
            index_col=0,
            parse_dates=[0],
        )["mean"]
        for c in countries
    }

    return data


def transform_panel(
    df: pd.DataFrame, fcn: Callable, columns: Optional[list] = None
) -> pd.DataFrame:
    """ Transform panel data via df.transform() for each country individually"""

    tmp_df = df.copy()

    # if single column given
    if isinstance(columns, str):
        columns = [columns]

    # long format
    if "country" in df.columns:
        countries = df["country"].unique()
        for c in countries:
            if columns is None:
                tmp_df.loc[tmp_df["country"] == c] = tmp_df.loc[
                    tmp_df["country"] == c
                ].transform(fcn)
            else:
                for col in columns:
                    tmp_df.loc[tmp_df["country"] == c, col] = tmp_df.loc[
                        tmp_df["country"] == c, col
                    ].transform(fcn)
        return tmp_df

    # wide format
    else:
        if columns is None:
            return tmp_df.transform(fcn)
        else:
            for col in columns:
                tmp_df[col] = tmp_df[col].transform(fcn)
            return tmp_df


# %%

# y = load_migration_rates_from_csv()
# x = load_trends_from_csv()
# data = Dataset(y, x)
# panel = data.create_panel()
# transform_panel

# transform_panel(panel, lambda df:(df - df.shift(1))/df.mean())

# %%
