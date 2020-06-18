import json
import random

import mwbase

from .content_transformer import ContentTransformer


class Wikidata2Words(ContentTransformer):
    @classmethod
    def from_siteinfo(cls, siteinfo, *args, **kwargs):
        return cls(*args, **kwargs)

    def transform(self, content):
        doc = json.loads(content)
        entity = mwbase.Entity.from_json(doc)
        claims_tuples = list(self._extract_property_values(entity))
        random.shuffle(claims_tuples)
        return claims_tuples

    @staticmethod
    def _extract_property_values(entity):
        properties = list(entity.properties.keys())
        for prop in properties:
            value_found = False
            for statement in entity.properties[prop]:
                claim = statement.claim
                if claim.datavalue is not None and \
                   claim.datavalue.type == 'wikibase-entityid':
                    datavalue = claim.datavalue
                    if datavalue:
                        value = datavalue.id
                        value_found = True
                        yield (prop, value)

            if not value_found:
                yield (prop,)
