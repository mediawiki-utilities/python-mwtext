class ContentTransformer:
    def transform(content):
        raise NotImplementedError()

    @classmethod
    def from_siteinfo(cls, siteinfo, *args, **kwargs):
        raise NotImplementedError()
