from verdictnet.ingestion.documentspec import DocumentSpec
from verdictnet.models.node import Node


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


def parse(tags, docspec: DocumentSpec, levels=None):
    """
    Parse a sequence of tags and return a list of elements of types defined in levels
    :param tags:
    :param docspec: DocumentSpec object that describes the schema of the document
    :param levels: Skip until this level is found, return collection of elements at this level
    :return: list of elements
    """
    requested_levels = []
    if levels is not None:
        requested_levels = [docspec.get_level_from_name(n) for n in levels]
        # Skip until we find the requested level
        while tags:
            # tag = tags[0]
            # cl = tag.get('class', [None])[0]

            cl = next_class(tags)
            if cl is not None and any([cl in level.attributes for level in requested_levels]):
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
        current_level = docspec.get_level_from_class(cl)
        if current_level is None:
            tags.remove(tags[0])
            continue

        attributes = {a: None for a in current_level.attributes}
        # Extract all attributes
        while cl in attributes.keys() and any(val is None for val in attributes.values()):
            tag = tags[0]
            attributes[cl] = tag.text
            tags.remove(tag)

            cl = next_class(tags)

        content = current_level.format.format(**attributes)

        obj = Node(
            level=current_level.level,
            content=content,
            children=[]
        )

        next_level = docspec.get_level_from_class(cl)
        # If there's no next level, we are at the end of the chain
        if next_level is None:
            # End of the chain
            elems.append(obj)
            return elems
        # Check if next level is child, sibling or parent
        if next_level.level in current_level.children:
            # Child
            obj.children = parse(tags, docspec=docspec, levels=current_level.children)
        elems.append(obj)

        next_level = docspec.get_level_from_class(next_class(tags))
        # If there's no next level, we are at the end of the chain
        if next_level is None:
            # End of the chain
            return elems
        if next_level.level in [current_level.level] + current_level.siblings + [l.level for l in
                                                                                 requested_levels]:
            # Same level
            pass

        else:  # Children ruled out because previous if already returned
            # Parent
            # wrap up and return
            return elems

    return elems
