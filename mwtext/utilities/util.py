import re
REDIRECT_RE = re.compile("#redirect", re.I)


def get_siteinfo(session):
    doc = session.get(action="query", meta="siteinfo",
                      siprop=["namespaces", "namespacealiases", "general"],
                      formatversion=2)
    return doc['query']


def is_relevant_page(page, revision, allowed_content_models=None,
                     allowed_namespaces=None, include_redirects=False,
                     min_content_length=None):
    if revision.text is None:
        return False
    if allowed_content_models:
        if revision.model not in allowed_content_models:
            return False
    if allowed_namespaces:
        if page.namespace not in allowed_namespaces:
            return False
    if not include_redirects:
        if REDIRECT_RE.match(revision.text):
            return False
    if min_content_length is not None:
        if len(revision.text) < min_content_length:
            return False

    return True
