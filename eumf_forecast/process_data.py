#%%
#
import os
import pandas as pd
import numpy as np
import glob
import json
import matplotlib.pyplot as plt


DATA_VERSION = "21-04-22"
files = glob.glob(f"raw_data/{DATA_VERSION}/*.csv")

LANGUAGE_ASSIGNMENT_FILE = "keywords/assignment_language_country.json"


def get_output_file(country: str) -> str:
    directory = f"processed_data/{DATA_VERSION}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(directory, f"processed_{country}.csv")


# retrieve countries of interest

#%%

with open(LANGUAGE_ASSIGNMENT_FILE) as f:
    assignment_language_country = json.load(f)

countries = assignment_language_country.keys()
# countries = ["HR"]


def plot_timeseries(df, col):
    df.plot(y=("mean", col))
    plt.fill_between(
        df.index,
        df["mean", col] - df["sem", col],
        df["mean", col] + df["sem", col],
        alpha=0.5,
    )
    plt.show()


for c in countries:

    print(c + "\n")

    files = glob.glob(f"raw_data/{DATA_VERSION}/data_{c}_*.csv")

    # read df from each file and concatenate
    df = pd.concat([pd.read_csv(f, index_col=0, parse_dates=[2]) for f in files])

    # average over iterations
    df = df.groupby(["date", "keyword_id"]).agg(["mean", "sem"])

    # resample
    df = df.groupby([pd.Grouper(level=0, freq="3M"), pd.Grouper(level=1)]).agg("mean")

    df = df.unstack(level=1)["value"]

    # convert keyword id to str
    df.columns.set_levels(df.columns.levels[1].astype(str), level=1, inplace=True)

    df.to_csv(get_output_file(c))

# %%
