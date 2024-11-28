import json
from dataclasses import dataclass, field
from typing import List


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
    name: str
    url: str
    schema: List[DocumentLevelSchema]
    tags: List[str]
    head: str

    @classmethod
    def from_dict(cls, data):
        return DocumentSpec(
            name=data['name'],
            url=data['url'],
            schema=[DocumentLevelSchema.from_dict(d) for d in data['schema']],
            tags=data['tags'],
            head=data['head']
        )

    def to_dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'schema': [d.to_dict() for d in self.schema],
            'tags': self.tags,
            'head': self.head
        }

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
