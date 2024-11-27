from models.node import Node

schema = [
    {
        'level': 'document',
        'name': 'Documento',
        'attributes': ['anexo'],
        'format': '{anexo}',
        'children': ['titulo', 'libro'],
    },
    {
        'level': 'libro',
        'name': 'Libro',
        'attributes': ['libro_num', 'libro_tit'],
        'format': '{libro_num}: {libro_tit}',
        'children': ['titulo', 'seccion'],
    },
    {
        'level': 'titulo',
        'name': 'Título',
        'attributes': ['titulo_num', 'titulo_tit'],
        'format': '{titulo_num}: {titulo_tit}',
        'children': ['capitulo', 'capitulo_unico', 'seccion', 'articulo']
    },
    {
        'level': 'capitulo',
        'name': 'Capítulo',
        'attributes': ['capitulo_num', 'capitulo_tit'],
        'format': '{capitulo_num}: {capitulo_tit}',
        'children': ['seccion', 'articulo', 'parrafo', 'parrafo2']
    },
    {
        'level': 'capitulo_unico',
        'name': 'Capítulo Unico',
        'attributes': ['capitulo'],
        'format': '{capitulo}',
        'children': ['seccion', 'articulo', 'parrafo', 'parrafo2']
    },
    {
        'level': 'seccion',
        'name': 'Sección',
        'attributes': ['seccion'],
        'format': '{seccion}',
        'children': ['subseccion', 'articulo']
    },
    {
        'level': 'subseccion',
        'name': 'Subsección',
        'attributes': ['subseccion'],
        'format': '{subseccion}',
        'children': ['articulo']
    },
    {
        'level': 'articulo',
        'name': 'Artículo',
        'attributes': ['articulo'],
        'format': '{articulo}',
        'children': ['parrafo', 'parrafo2']
    },
    {
        'level': 'parrafo',
        'name': 'Párrafo',
        'attributes': ['parrafo'],
        'format': '{parrafo}',
        'children': ['footnote'],
        'siblings': ['parrafo2']
    },
    {
        'level': 'parrafo2',
        'name': 'Párrafo2',
        'attributes': ['parrafo_2'],
        'format': '{parrafo_2}',
        'children': ['footnote'],
        'siblings': ['parrafo']
    },
    {
        'level': 'footnote',
        'name': 'Cita',
        'attributes': ['cita_con_pleca'],
        'format': '{cita_con_pleca}',
        'children': []
    }
]


def get_level_from_class(attr):
    """
    Given a tag class, return the level it is an attribute of
    :param attr:
    :return:
    """
    for level in schema:
        if attr in level['attributes']:
            return level
    return None


def get_level_from_name(name):
    """
    Given a tag class, return the level it is an attribute of
    :param attr:
    :return:
    """
    for level in schema:
        if name == level['level']:
            return level
    return None


def next_class(tags):
    """
    Scan the tags head to find the next hierarchy level, if any
    :param tags:
    :return:
    """
    try:
        tag = tags[0]
        cl = tag.get('class')[0]
    except IndexError:
        cl = None
    except TypeError:
        cl = None

    return cl


def parse(tags, levels=None):
    """
    Parse a sequence of tags and return a list of elements of types defined in levels
    :param tags:
    :param levels: Skip until this level is found, return collection of elements at this level
    :return: list of elements
    """
    requested_levels = []
    if levels is not None:
        requested_levels = [get_level_from_name(n) for n in levels]
        # Skip until we find the requested level
        while tags:
            # tag = tags[0]
            # cl = tag.get('class', [None])[0]

            cl = next_class(tags)
            if cl is not None and any([cl in level['attributes'] for level in requested_levels]):
                break
            tag = tags[0]
            tags.remove(tag)

    elems = []

    while tags:
        # Is next tag a child, sibling or parent?
        # Child? -> Parse children
        # Sibling? -> Consume tags and append
        # Parent? -> Return

        cl = next_class(tags)
        # Determine what level we are at
        current_level = get_level_from_class(cl)
        if current_level is None:
            tags.remove(tags[0])
            continue

        attributes = {a: None for a in current_level['attributes']}
        # Extract all attributes
        while cl in attributes.keys() and any(val is None for val in attributes.values()):
            tag = tags[0]
            attributes[cl] = tag.text
            tags.remove(tag)

            cl = next_class(tags)

        content = current_level['format'].format(**attributes)

        obj = Node(
            level=current_level['level'],
            content=content,
            children=[]
        )

        next_level = get_level_from_class(cl)
        # If there's no next level, we are at the end of the chain
        if next_level is None:
            # End of the chain
            elems.append(obj)
            return elems
        # Check if next level is child, sibling or parent
        if next_level['level'] in current_level['children']:
            # Child
            obj.children = parse(tags, levels=current_level['children'])
        elems.append(obj)

        next_level = get_level_from_class(next_class(tags))
        # If there's no next level, we are at the end of the chain
        if next_level is None:
            # End of the chain
            return elems
        if next_level['level'] in [current_level['level']] + current_level.get('siblings', []) + [l['level'] for l in
                                                                                                  requested_levels]:
            # Same level
            pass

        else:  # Children ruled out because previous if already returned
            # Parent
            # wrap up and return
            return elems

    return elems
