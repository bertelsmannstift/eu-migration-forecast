#%%
#
import os
import pandas as pd
import glob
import json
import argparse

import logging
import logging.config

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)

from modules.eumf_google_trends import get_trends_output_filename
from modules.eumf_data import get_processed_trends_filename

DATA_VERSION = "21-04-22"
LANGUAGE_ASSIGNMENT_FILE = "data/config/assignment_language_country.json"

parser = argparse.ArgumentParser(
    description="Obtain data from Google Trends API and store them in csv files."
)

parser.add_argument(
    "-d",
    "--data_version",
    type=str,
    default="default",
    help="name of the version of the raw data to be used for processing",
)
parser.add_argument(
    "-d",
    "--data_version",
    type=str,
    default="default",
    help="name of the version of the raw data to be used for processing",
)

args, unknown = parser.parse_known_args()


#%%

with open(LANGUAGE_ASSIGNMENT_FILE) as f:
    assignment_language_country = json.load(f)

countries = assignment_language_country.keys()


for c in countries:

    print(c + "\n")

    files = glob.glob(f"data/raw/trends/{DATA_VERSION}/data_{c}_*.csv")

    # read df from each file and concatenate
    df = pd.concat([pd.read_csv(f, index_col=0, parse_dates=[2]) for f in files])

    # average over iterations
    df = df.groupby(["date", "keyword_id"]).agg(["mean", "sem"])

    # resample
    # df = df.groupby([pd.Grouper(level=0, freq="3M"), pd.Grouper(level=1)]).agg("mean")

    df = df.unstack(level=1)["value"]

    # convert keyword id to str
    df.columns.set_levels(df.columns.levels[1].astype(str), level=1, inplace=True)

    df.to_csv(get_processed_trends_filename(c, args.data_version))

# %%
