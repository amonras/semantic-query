import json
import uuid
from dataclasses import dataclass
from typing import List


class AutoIncrement:  # pylint: disable=too-few-public-methods
    """
    Implement an auto-incrementing id
    """
    id: int
    _id_counter = 1

    def __post_init__(self):
        self.id = self.__class__._id_counter  # pylint: disable=protected-access
        self.__class__._id_counter += 1


@dataclass
class Node(AutoIncrement):
    level: str
    content: str
    children: list
    id: int = None
    uuid: str = None

    def __post_init__(self):
        super().__post_init__()
        if self.uuid is None:
            self.uuid = str(uuid.uuid4())

    def __repr__(self):
        return f'{self.level}({self.content})'

    def render(self, level=0):
        """
        Return text string representation of the node and its children
        """
        indent = '  ' * level
        text = f'{indent}{self.content}'
        for child in self.children:
            text += "\n" + child.render(level + 1)
        return text

    def html(self, preamble=''):
        """
        Return a collapsable representation of the node
        """
        out = preamble
        if not self.children:
            out += f'<p id="{self.uuid}">{self.content}</p>'
        else:
            out += f"""
            <details id="{self.uuid}">
                <summary>{self.content}</summary>
                <ul>
                    {''.join([child.html() for child in self.children])}
                </ul>
            </details>
        """
        return out

    def json(self):
        """
        Return a json representation of the node
        """
        return {
            'id': self.id,
            'uuid': self.uuid,
            'level': self.level,
            'content': self.content,
            'children': [child.json() for child in self.children]
        }

    def save(self, path):
        """
        Save the node to a file
        """
        with open(path, 'w', encoding='utf8') as file:
            json.dump(self.json(), file, indent=4, ensure_ascii=False)

    def load(self, path):
        """
        Load the node from a file
        """
        with open(path, 'r', encoding='utf8') as file:
            data = json.load(file, ensure_ascii=False)
        return Node(**data)

    @classmethod
    def from_dict(cls, data):
        """
        Create a node from a dictionary
        """
        return Node(
            id=data['id'],
            level=data['level'],
            content=data['content'],
            children=[cls.from_dict(child) for child in data['children']]
        )

    def get_all(self, level) -> List['Node']:
        """
        Get all nodes of a certain level
        """
        if self.level == level:
            return [self]
        nodes = []
        for child in self.children:
            nodes.extend(child.get_all(level))
        return nodes
