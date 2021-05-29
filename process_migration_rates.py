import pandas as pd
import json
import datetime as dt
import warnings
import os
import sys
import glob
import argparse

parser = argparse.ArgumentParser(
    description="Process Excel files from DESTATIS with migration data."
)

parser.add_argument(
    "--year", "-y", type=int, help="year used (default: all in years.json)"
)

parser.add_argument(
    "--reset", "-r", action="store_true", help="delete ouput file before reading"
)

args = parser.parse_args()

DIR = "migration_rates"
OUTPUT_FILE = "migration_rate_processed.csv"
COUNTRY_CONFIG_FILE = "countries.json"
YEAR_CONFIG_FILE = "years.json"

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

with open(os.path.join(DIR, COUNTRY_CONFIG_FILE)) as buf:
    countries = json.load(buf)

with open(os.path.join(DIR, YEAR_CONFIG_FILE)) as buf:
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
        os.remove(os.path.join(DIR, OUTPUT_FILE))
    except:
        pass

for key, conf in selected_configs.items():

    y = int(key)
    usecols = conf["usecols"]

    print(key, conf)

    # read existing output file, otherwise create new df
    try:
        data = pd.read_csv(os.path.join(DIR, OUTPUT_FILE), index_col=0)
    except:
        data = pd.DataFrame(columns=["date", "country", "value"])

    data["date"] = pd.to_datetime(data["date"])

    # remove all entries from given year if existing
    data = data[data["date"].dt.year != y]

    for m, m_name in MONTHS.items():

        print(m_name)

        date = dt.datetime(y, m, 1)
        df_tmp = pd.read_excel(
            os.path.join(DIR, conf["filename"]),
            sheet_name=m_name,
            usecols=usecols,
            skiprows=2,
            nrows=172,
        )

        df_tmp.columns = ["country", "value"]

        for c, c_name in countries.items():
            try:
                value = df_tmp[df_tmp["country"] == c_name]["value"].iloc[0]
            except:
                warnings.warn(f"No data for country {c_name}")
                continue

            data = data.append(
                {"date": date, "country": c, "value": value}, ignore_index=True
            )

    data.sort_values(by="date").to_csv(os.path.join(DIR, OUTPUT_FILE))
