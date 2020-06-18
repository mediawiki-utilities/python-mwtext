from mwapi.session import Session

wiki_host = "https://en.wikipedia.org"
session = Session(wiki_host, user_agent="mwtext scripts get_siteinfo")
doc = session.get(
    action="query",
    meta="siteinfo",
    siprop=["namespaces", "namespacealiases", "general"],
    formatversion=2
)
siteinfo = doc["query"]
