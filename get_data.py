# %%
#
import json
import pandas as pd
import os
import argparse

from modules.eumf_google_trends import (
    GoogleTrendsConnector,
    prepare_searchwords,
    get_trends,
    trends_to_csv,
    get_trends_output_filename,
)

import logging
import logging.config

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)

KEYWORD_FILE = "data/keywords/keywords-prototype-21-04-22.xlsx"
LANGUAGE_ASSIGNMENT_FILE = "data/config/assignment_language_country.json"
GERMANY_TRANSLATION_FILE = "data/config/germany_language_keywords.json"

parser = argparse.ArgumentParser(
    description="Obtain data from Google Trends API and store them in csv files."
)

parser.add_argument(
    "--start_iteration",
    type=int,
    help="no. of the first iteration of datasets to draw",
    default=0,
)
parser.add_argument(
    "--n_iterations", type=int, default=1, help="no. of datasets to draw"
)
parser.add_argument(
    "-d",
    "--data_version",
    type=str,
    default="default",
    help="arbitrary string to name the version of the data drawn",
)
parser.add_argument(
    "-f", "--force", action="store_true", help="draw also existing datasets"
)
parser.add_argument(
    "--start_date", type=str, default="2007-01", help="datestring for earliest date"
)
parser.add_argument(
    "--end_date", type=str, default="2020-12", help="datestring for last date"
)
parser.add_argument(
    "--countries",
    type=str,
    nargs="+",
    help="limit countries of origin to draw data for (2 letter ISO code)",
    default=[],
)

args, unknown = parser.parse_known_args()


#%%

trends = GoogleTrendsConnector()

df_keywords = pd.read_excel(KEYWORD_FILE)
df_keywords = df_keywords.loc[~df_keywords["KeywordID"].isna()]
df_keywords["KeywordID"] = df_keywords["KeywordID"].astype(int)
df_keywords = df_keywords.melt(
    id_vars=["KeywordID", "FlagWithoutGermany"],
    var_name="language_id",
    value_name="keyword",
).rename(columns={"KeywordID": "keyword_id", "FlagWithoutGermany": "without_germany"})
df_keywords.loc[~df_keywords["without_germany"].isna(), "without_germany"] = True
df_keywords.loc[df_keywords["without_germany"].isna(), "without_germany"] = False
df_keywords["version_id"] = 1


with open(LANGUAGE_ASSIGNMENT_FILE) as f:
    assignment_language_country = json.load(f)

tmp_assignments = []
for country, arr in assignment_language_country.items():
    for lan in arr:
        tmp_assignments.append([country, lan])
df_assignments = pd.DataFrame(tmp_assignments, columns=["country_id", "language_id"])

df_countries = (
    df_assignments[["country_id"]]
    .rename(columns={"country_id": "id"})
    .drop_duplicates()
)
df_countries["short"] = df_countries["id"]

with open(GERMANY_TRANSLATION_FILE) as f:
    germany_language_keywords = json.load(f)

df_languages = (
    pd.Series(germany_language_keywords)
    .rename("germany")
    .to_frame()
    .rename_axis(index="id")
    .reset_index()
)
df_languages["short"] = df_languages["id"]
df_languages["remove_diacritics"] = False
for l in ["PL", "CS", "SK", "FR", "EL", "HR", "IT", "LV", "LI", "PT", "ES"]:
    df_languages.loc[df_languages["short"] == l, "remove_diacritics"] = True


logger.info("Prepare Searchwords...")

df_searchwords = prepare_searchwords(df_keywords, df_assignments, df_languages)
df_searchwords = df_searchwords.merge(df_countries, left_on="country_id", right_on="id")

#%%
countries = (
    args.countries if len(args.countries) > 0 else list(df_countries["short"].unique())
)

logger.info("Get Trends...")

for iteration in range(args.start_iteration, args.start_iteration + args.n_iterations):

    logger.info("Iteration %d", iteration)

    for country in countries:

        if not args.force and os.path.exists(
            get_trends_output_filename(country, args.data_version, iteration)
        ):
            continue

        logger.info(f"Get data for country {country}")
        tmp_searchwords = df_searchwords[df_searchwords["short"] == country]
        df_responses = get_trends(
            trends, tmp_searchwords, args.start_date, args.end_date
        )
        trends_to_csv(
            df_responses, df_searchwords, country, args.data_version, iteration
        )


# %%
