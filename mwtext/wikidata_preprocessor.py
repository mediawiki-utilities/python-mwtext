class WikidataPreprocessor:
    def process(self, entity):
        return list(self._extract_property_values(entity))

    @staticmethod
    def _extract_property_values(entity):
        properties = list(entity.properties.keys())
        for prop in properties:
            value_found = False
            for statement in entity.properties[prop]:
                claim = statement.claim
                if claim.datavalue is not None and claim.datavalue.type == 'wikibase-entityid':
                    datavalue = claim.datavalue
                    if datavalue:
                        value = datavalue.id
                        value_found = True
                        yield (prop, value)

            if not value_found:
                yield (prop,)
