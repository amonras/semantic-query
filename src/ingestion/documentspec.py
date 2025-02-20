import json
from dataclasses import dataclass, field
from typing import List

from slugify import slugify


@dataclass
class DocumentLevelSchema:
    name: str
    level: str
    attributes: List[str]
    format: str
    children: List[str]
    siblings: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        return DocumentLevelSchema(
            name=data['name'],
            level=data['level'],
            attributes=data['attributes'],
            format=data['format'],
            children=data['children'],
            siblings=data.get('siblings', [])
        )

    def to_dict(self):
        obj = {
            'name': self.name,
            'level': self.level,
            'attributes': self.attributes,
            'format': self.format,
            'children': self.children,
        }
        if self.siblings:
            obj['siblings'] = self.siblings

        return obj


@dataclass
class DocumentSpec:
    name: str  # The name of the document/dataset
    url: str  # The url where the document can be found
    schema: List[DocumentLevelSchema]  # The schema of the document
    tags: List[str]  # The html tag types that need to be observed in order to parse the document
    head: str  # The head of the document, to be used for the root node at root.level
    embed_level: str  # The level at which the document should be embedded in the database
    wraps: List[str] = field(default_factory=list)  # The levels that should be wrapped immediately under the root node

    @classmethod
    def from_dict(cls, data):
        return DocumentSpec(
            name=data['name'],
            url=data['url'],
            schema=[DocumentLevelSchema.from_dict(d) for d in data['schema']],
            tags=data['tags'],
            head=data['head'],
            embed_level=data['embed_level'],
            wraps=data.get('wraps', [])
        )

    def to_dict(self):
        obj = {
            'name': self.name,
            'url': self.url,
            'schema': [d.to_dict() for d in self.schema],
            'tags': self.tags,
            'head': self.head,
            'embed_level': self.embed_level,
        }
        if self.wraps:
            obj['wraps'] = self.wraps

        return obj

    @classmethod
    def load(cls, filename):
        with open(filename, 'r') as file:
            return DocumentSpec.from_dict(json.load(file))

    def dumps(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)

    def dump(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, indent=4)

    def get_level_from_class(self, attr):
        """
        Given a tag class, return the level it is an attribute of
        :param attr:
        :return:
        """
        for level in self.schema:
            if attr in level.attributes:
                return level
        return None

    def get_level_from_name(self, name):
        """
        Given a name, return the schema for the level
        :param name:
        :return:
        """
        for level in self.schema:
            if name == level.level:
                return level
        return None

    @property
    def code(self):
        return slugify(self.name)
