NON_LINK_NAMESPACES = (6, 14)


def generate_non_link_namespace_names(siteinfo):
    non_link_namespace_names = set()
    for namespace in siteinfo['namespaces'].values():
        if namespace['id'] in NON_LINK_NAMESPACES:
            non_link_namespace_names.add(namespace['name'].lower())
            non_link_namespace_names.add(namespace['canonical'].lower())
    for namespace in siteinfo['namespacealiases']:
        if namespace['id'] in NON_LINK_NAMESPACES:
            non_link_namespace_names.add(namespace['alias'].lower())

    return non_link_namespace_names
