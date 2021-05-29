#%%
from matplotlib import pyplot as plt
from apiclient.discovery import build
import pandas as pd

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


def get_response(term, geo):
    print(term)
    return pd.DataFrame(
        service.getGraph(
            terms=term,
            restrictions_startDate=start_date,
            restrictions_endDate=end_date,
            restrictions_geo=geo,
        ).execute()["lines"][0]["points"]
    ).assign(**{"country": geo, "term": term})


#%%

df_trends = get_response("trabalhar alemanha + trabalho alemanha", "PT")
df_trends["date"] = pd.to_datetime(df_trends["date"])
df_trends.set_index("date", inplace=True)

dates = [
    "2004-01-01",
    "2005-01-01",
    "2006-01-01",
    "2007-01-01",
    "2008-01-01",
    "2009-01-01",
    "2010-01-01",
    "2011-01-01",
    "2012-01-01",
    "2013-01-01",
    "2014-01-01",
    "2015-01-01",
    "2016-01-01",
    "2017-01-01",
    "2018-01-01",
]
values = [
    5070,
    5010,
    5001,
    5516,
    5911,
    6779,
    6513,
    8297,
    11820,
    13635,
    11394,
    10145,
    9755,
    8952,
    8314,
]
df_destatis = pd.DataFrame({"date": dates, "value": values})
df_destatis["date"] = pd.to_datetime(df_destatis["date"])
df_destatis.set_index("date", inplace=True)

# %%
plt.figure()
ax = df_destatis["value"].plot(color="tab:blue")
# ax2 = ax.twinx()
df_trends["value"].resample("Y").sum().plot(
    ax=ax, label="bla", secondary_y=True, color="tab:orange"
)
ax.set_ylabel("annual registrations")
ax.right_ax.set_ylabel("Google Trends Index")
# df_trends.plot(ax = ax2)
# plt.show()
# %%
