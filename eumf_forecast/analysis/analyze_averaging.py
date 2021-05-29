#%%
#
import pprint
import pandas as pd
import numpy as np
import random
import string
import matplotlib.pyplot as plt
from apiclient.discovery import build
from googleapiclient.errors import HttpError

pd.set_option("display.max_rows", 200)


#%%
SERVER = "https://trends.googleapis.com"

API_VERSION = "v1beta"
DISCOVERY_URL_SUFFIX = "/$discovery/rest?version=" + API_VERSION
DISCOVERY_URL = SERVER + DISCOVERY_URL_SUFFIX


service = build(
    "trends",
    "v1beta",
    developerKey="AIzaSyANmyabv5zka2cg0hj07BRiJPMgH6lxM4A",
    discoveryServiceUrl=DISCOVERY_URL,
)

start_date = "2004-01"
end_date = "2020-12"

#%%
def rand_str(chars=string.ascii_uppercase + string.digits, N=10):
    return "".join(random.choice(chars) for _ in range(N))


def get_response(term, geo, anchor=None):

    print(term)

    response = service.getGraph(
        terms=[term, anchor] if anchor is not None else [term],
        restrictions_startDate=start_date,
        restrictions_endDate=end_date,
        restrictions_geo=geo,
    ).execute()["lines"][0]["points"]

    return (
        pd.DataFrame(response)
        .assign(**{"country": geo, "term": term})
        .astype({"date": "datetime64"})
    )


def get_sample(term, geo, n_req, anchor=None):
    keywords = [term + " + " + rand_str() for i in range(n_req)]
    responses = []
    for i, k in enumerate(keywords):
        try:
            response = get_response(k, country, anchor)
            response["response_id"] = i
            responses.append(response)
        except HttpError as err:
            print(err)
            break
    return pd.concat(responses)


#%%
# small countries - requests by averaging?

country = "EE"
# query = "job germany + jobs germany + job deutschland + jobs deutschland + työ saksa + työpaikka saksa + työt saksa + työpaikat saksa" #fi result true - true - true
# query = "job germany + jobs germany + job deutschland + jobs deutschland + delovno mesto nemčija + delovna mesta nemčija" #si result true - false - false
# query = "job germany + jobs germany + job deutschland + jobs deutschland + darbs vācija + darbi vācija + darbs vacija + darbi vacija" #lv result - true - true
query = "job germany + jobs germany + job deutschland + jobs deutschland + töökoht saksamaa + töökohad saksamaa"  # ee - result false false
anchor = "bielefeld"
n_req = 10

df_all_ = get_sample(query, country, n_req, anchor)

df_agg_ = df_all_[["value", "date"]].groupby("date").agg("mean")

df_agg_

#%%
# which sample size? - requests

country = "FI"
query = "job germany + jobs germany"
anchor = "dresden"
n_req = 100

df_all = get_sample(query, country, n_req, anchor)

df_all.groupby("response_id").max()

#%%
# which sample size? - analysis
levels = [10, 100]
freq = "3M"

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(1, 1, 1)
for n in levels:
    df_tmp = (
        df_all[df_all["response_id"] < n]
        .groupby([pd.Grouper(key="date", freq=freq), pd.Grouper(key="response_id")])
        .mean()
    )

    df_tmp.groupby(level="date").agg("mean").plot(ax=ax)

    y = df_tmp.groupby(level="date").agg("mean")["value"]
    d = df_tmp.groupby(level="date").agg("mean").index.to_pydatetime()
    e = df_tmp.groupby(level="date").agg("sem")["value"]

    plt.fill_between(d, y-e, y+e, interpolate=True, alpha=0.75)

#    plt.plot_date(d, y, "-", label = f"n={n}")
#    print(d)
    #plt.plot_date(df_tmp.groupby(level="date").agg("mean").index,df_tmp.groupby(level="date").agg("mean")["value"])
    # plt.fill_between(df_tmp.groupby(level="date").agg("mean"), data['A'], data['B'],
    #             where=data['A'] >= data['B'],
    #             facecolor='green', alpha=0.2, interpolate=True)
ax.legend([f"n={n}" for n in levels])
plt.title(f"keyword: {query}, country: {country}, anchor: {anchor}, sampling freq: {freq}")

# %%

df_aggs = []

for i in range(3):
    keywords = [
        "apartment germany + flat germany + room germany + " + rand_str()
        for i in range(100)
    ]
    df_all = pd.concat([get_response(k, country, anchor) for k in keywords]).assign(
        **{"language": "EN"}
    )
    df_aggs.append(df_all[["value", "date"]].groupby("date").agg("mean"))

# %%
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(1, 1, 1)
for df in df_aggs:
    df.plot(ax=ax)
plt.title(
    "'apartment germany + flat germany + room germany', IE, 100 requests, anchor: 'merkel'"
)
plt.show()
# %%
