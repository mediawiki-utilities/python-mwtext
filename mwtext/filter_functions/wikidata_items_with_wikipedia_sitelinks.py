import json
from pkg_resources import resource_filename

import mwbase


filepath = resource_filename('mwtext', 'assets/wikimedia_internal_item_qids.txt')
with open(filepath) as f:
    wm_internal_items = [line.rstrip('\n') for line in f]


def include(page, revision):
    # Namespace zero
    if page.namespace != 0 or revision.model != 'wikibase-item':
        return False

    item_doc = json.loads(revision.text)
    qid = item_doc.get('id', None)
    redirect = item_doc.get('redirect')
    entity = mwbase.Entity.from_json(item_doc)

    # Redirects to other Wikidata item
    if redirect is not None:
        return False

    # Has a Qid
    if qid is None:
        return False

    # Sitelinks to a Wikipedia of any language
    sitelinks = any((llink not in ('commonswiki',
                     'specieswiki', 'metawiki', 'testwiki') and
                     llink.endswith("wiki"))
                    for llink in entity.sitelinks)

    if not sitelinks:
        return False

    # Is subclass of Wikimedia internal item
    if qid in wm_internal_items:
        return False

    # Is instance-of Wikimedia internal item or its subclasses
    properties = entity.properties
    instanceof_property = 'P31'
    for statement in properties.get(instanceof_property, []):
        claim = statement.claim
        if claim.datavalue is not None and \
           claim.datavalue.type == 'wikibase-entityid':
            value = claim.datavalue.id
            if value in wm_internal_items:
                return False

    return True
