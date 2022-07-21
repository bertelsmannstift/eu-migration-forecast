import pandas as pd
import json
import datetime as dt
from tqdm import tqdm
import os
import argparse

#TODO: use DESTATIS API instead of excel files

parser = argparse.ArgumentParser(
    description="Process Excel files from DESTATIS with migration data."
)

parser.add_argument(
    "--year",
    "-y",
    type=int,
    help="Year used (default: all in years.json). "
    "Existing years will be replaced in the output file.",
)

parser.add_argument(
    "--reset", "-r", action="store_true", help="Delete ouput file before reading."
)

args = parser.parse_args()

INPUT_DIR = "data/raw/registrations"
OUTPUT_DIR = "data/processed/registrations"
CONFIG_DIR = "data/config"
OUTPUT_FILE = "registrations_processed.csv"
COUNTRY_CONFIG_FILE = "country_names_registrations.json"
YEAR_CONFIG_FILE = "years_registrations.json"

MONTHS = {
    1: "Januar",
    2: "Februar",
    3: "März",
    4: "April",
    5: "Mai",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Dezember",
}

with open(os.path.join(CONFIG_DIR, COUNTRY_CONFIG_FILE)) as buf:
    countries = json.load(buf)

with open(os.path.join(CONFIG_DIR, YEAR_CONFIG_FILE)) as buf:
    year_configs = json.load(buf)

if args.year is not None:
    # years = [args.year]
    # input_files = [year_configs[str(args.year)]["filename"]]
    selected_configs = {k: year_configs[k] for k in [str(args.year)]}
else:
    # years = [int(k) for k in year_configs.keys()]
    # input_files = [v["filename"] for v in year_configs.values()]
    selected_configs = year_configs

if args.reset:
    try:
        os.remove(os.path.join(OUTPUT_DIR, OUTPUT_FILE))
    except:
        pass

for key, conf in selected_configs.items():

    y = int(key)
    usecols = conf["usecols"]

    print(key, conf)

    # read existing output file, otherwise create new df
    try:
        data = pd.read_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE), index_col=0)
    except:
        data = pd.DataFrame(columns=["date", "country", "value"])

    data["date"] = pd.to_datetime(data["date"])

    # remove all entries from given year if existing
    data = data[data["date"].dt.year != y]

    for m, m_name in tqdm(MONTHS.items(), desc=key):

        date = dt.datetime(y, m, 1)
        df_tmp = pd.read_excel(
            os.path.join(INPUT_DIR, conf["filename"]),
            sheet_name=m_name,
            usecols=usecols,
            skiprows=2,
            nrows=172,
        )
        df_tmp.columns = ["country", "value"]

        if "correction_filename" in conf.keys():
            df_corr = pd.read_excel(
                os.path.join(INPUT_DIR, conf["correction_filename"]),
                sheet_name=m_name,
                usecols=usecols,
                skiprows=2,
                nrows=172,
            )
            df_corr.columns = ["country", "value"]
        else:
            df_corr = None

        for c, c_name in countries.items():
            cond = df_tmp["country"].str.contains(c_name, na=False)
            values = df_tmp[cond]["value"].iloc[0]
            if df_corr is not None:
                corrections = df_corr[cond]["value"].iloc[0]
                # values = values.astype(float) - corrections.astype(float)
                values -= corrections

            data = data.append(
                {"date": date, "country": c, "value": values}, ignore_index=True
            )

    data.sort_values(by="date").to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE))
