class WikidataPreprocessor:
    def process(self, entity):
        properties = list(entity.properties.keys())
        for prop in properties:
            value_found = False
            for statement in entity.properties[prop]:
                claim = statement.claim
                if claim.datatype == 'wikibase-item':
                    datavalue = claim.datavalue
                    if datavalue:
                        value = datavalue.id
                        value_found = True
                        yield (prop, value)

            if not value_found:
                yield (prop,)
