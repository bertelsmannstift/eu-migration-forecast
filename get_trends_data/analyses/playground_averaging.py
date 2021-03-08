#%%
#
import pprint
import pandas as pd
import numpy as np
import random
import string
import matplotlib.pyplot as plt
from apiclient.discovery import build

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


#%%

country = "EE"
#query = "job germany + jobs germany + job deutschland + jobs deutschland + työ saksa + työpaikka saksa + työt saksa + työpaikat saksa" #fi
#query = "job germany + jobs germany + job deutschland + jobs deutschland + delovno mesto nemčija + delovna mesta nemčija" #si
#query = "job germany + jobs germany + job deutschland + jobs deutschland + darbs vācija + darbi vācija + darbs vacija + darbi vacija" #lv
query = "job germany + jobs germany + job deutschland + jobs deutschland + töökoht saksamaa + töökohad saksamaa" #lv
anchor = "bielefeld"
n_req = 50


def get_response(term, geo, anchor=None):
    print(term)
    return pd.DataFrame(
        service.getGraph(
            terms=[term, anchor] if anchor is not None else [term],
            restrictions_startDate=start_date,
            restrictions_endDate=end_date,
            restrictions_geo=geo,
        ).execute()["lines"][0]["points"]
    ).assign(**{"country": geo, "term": term})


keywords = [query + " + " + rand_str() for i in range(n_req)]

df_all = pd.concat([get_response(k, country, anchor) for k in keywords])

df_agg = df_all[["value", "date"]].groupby("date").agg("mean")

df_agg
# %%
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(1, 1, 1)
df_agg.plot(ax=ax)
plt.title(", ".join([query, country, str(n_req) + "requests", "anchor: " + anchor]))
plt.show()
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
