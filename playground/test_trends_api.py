#%%
#
import pprint
from apiclient.discovery import build

#%%
SERVER = "https://trends.googleapis.com"

API_VERSION = "v1beta"
DISCOVERY_URL_SUFFIX = "/$discovery/rest?version=" + API_VERSION
DISCOVERY_URL = SERVER + DISCOVERY_URL_SUFFIX


def main():
    service = build(
        "trends",
        "v1beta",
        developerKey="AIzaSyANmyabv5zka2cg0hj07BRiJPMgH6lxM4A",
        discoveryServiceUrl=DISCOVERY_URL,
    )

    # # Single Graph Example, no restrictions
    # graph = service.getGraph(terms="apple")
    # response = graph.execute()
    # pprint.pprint(response)

    # # Averages, no restrictions.
    # averages = service.getGraphAverages(terms=["apple", "orange"])
    # response = averages.execute()
    # pprint.pprint(response)

    # # Regions, no restrictions.
    # regions = service.regions().list(term="apple")
    # response = regions.execute()
    # pprint.pprint(response)

    # # Top queries, no restrictions.
    # top_queries = service.getTopQueries(term="apple")
    # response = top_queries.execute()
    # pprint.pprint(response)

    # # Top topics, no restrictions.
    # # The result for topics (top & rising) is a list of knowledge graph
    # # topics (entity ids - mids), which can be resolved using freebase.com
    # top_topics = service.getTopTopics(term="apple")
    # response = top_topics.execute()
    # pprint.pprint(response)

    # # Note that returned values for rising queries and topics represents
    # # percentage of rising in searches since previous time range. If there
    # # were close to 0 searches for the term in the previous time range, the
    # # value will be Double.MAX_VALUE and considered "breakout".

    # # Rising queries, no restrictions.
    # rising_queries = service.getRisingQueries(term="apple")
    # response = rising_queries.execute()
    # pprint.pprint(response)

    # Rising topics, no restrictions.
    # rising_topics = service.getRisingTopics(term="apple")
    # response = rising_topics.execute()
    # pprint.pprint(response)

    # Creating restrictions.
    # Note that you need both a startDate and an endDate or none.
    # Dates should be a month and a year in the format YYYY-MM e.g. '2010-01'
    # Parameter names are: restrictions_startDate, restrictions_endDate.
    #
    # Geo takes any of the values depicted here:
    #   http://en.wikipedia.org/wiki/ISO_3166-2#Current_codes
    # Parameter name is restrictions_geo.
    #
    # Category takes the following value formats:
    #   0-3 is Arts & Entertainment
    #   0-3-613 is Online Media (which is a subcategory of the above).
    # We will do our best to fix you up with a list of possible codes, but in
    # the meantime, you can query each such category in the Trends Explore
    # frontend, by hitting on "embed" after you've chosen a category for
    # a query and copying what's written next to: &cat=
    # Parameter name is restrictions_category.
    #
    # Property takes the values: images/news/froogle/youtube/web
    # Web is the default value if none is provided, and 'froogle' is
    # Google Shopping.
    # Parameter name is restrictions_property.

    

    start_date = "2004-01"
    end_date = "2020-12"
    response = service.getGraph(
        terms="brexit",
        restrictions_startDate=start_date,
        restrictions_endDate=end_date,
        restrictions_geo="SE",
    ).execute()
    pprint.pprint(response)

    # All methods allow term to be either search query or knowledge graph
    # topic id (mid) - use freebase.com to find these ids.
    # response = service.getGraph(terms="/m/02mjmr").execute()
    # pprint.pprint(response)


if __name__ == "__main__":
    main()


# %%
