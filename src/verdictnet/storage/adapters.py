from typing import Optional

import numpy as np

from verdictnet.models.node import Node


class NodeAdapter:
    @staticmethod
    def to_neo4j(node: Node, ordinal: Optional[int] = None):
        out = {
            'uuid': node.uuid,
            'ordinal': ordinal,
            'level': node.level,
            'content': node.content
        }

        return out

    @staticmethod
    def to_neo4j_with_relationships(node: Node, ordinal: Optional[int] = None):
        """
        Recursively extract all nodes and relationships from a hierarchy.

        Args:
            node (Node): The root node of the hierarchy.
            ordinal (Optional[int]): The ordinal value of the node in its parent's children list.

        Returns:
            - nodes: List of dictionaries representing nodes.
            - relationships: List of tuples representing (parent_uuid, child_uuid) relationships.
        """
        nodes = []
        relationships = []

        # Convert the root node
        nodes.append(NodeAdapter.to_neo4j(node, ordinal))

        # Recursively process children
        for child_ordinals, child in enumerate(node.children):
            # Add the relationship to child
            relationships.append((node.uuid, child.uuid))

            # Add grand child's nodes and relationships
            child_nodes, child_relationships = NodeAdapter.to_neo4j_with_relationships(child, child_ordinals)
            nodes.extend(child_nodes)  # Append all child nodes
            relationships.extend(child_relationships)  # Append all child relationships

        return nodes, relationships

    @classmethod
    def from_neo4j(cls, record: dict) -> Node:
        if record.get('children', []):
            children, order = zip(*[[cls.from_neo4j(ch), ch['ordinal']] for ch in record.get('children', [])])

            order = np.array([o if o is not None else np.inf for o in order])

            np.argsort(order)

            sorted_children = list(np.array(children)[np.argsort(order)])
        else:
            sorted_children = []
        return Node(
            uuid=record['uuid'],
            level=record['level'],
            content=record['content'],
            children=sorted_children
        )

    @staticmethod
    def build_hierarchy(root_uuid: str, nodes: dict) -> Node:
        """
        Build a Node hierarchy from a flat structure.

        Args:
            root_uuid (str): The UUID of the root node.
            nodes (dict): Dictionary of all nodes keyed by UUID.

        Returns:
            Node: Root Node with children populated.
        """
        node_data = nodes[root_uuid]
        root_node = Node(
            uuid=node_data['uuid'],
            level=node_data['level'],
            content=node_data['content'],
            children=[]
        )

        stack = [(root_node, root_uuid)]
        temp_nodes = {
            uuid: data
            for uuid, data in nodes.items()
        }

        for uuid, data in nodes.items():
            parent_uuid = data.get('parent_uuid')
            if parent_uuid is None:
                continue
            parent_data = temp_nodes.get(parent_uuid, {})
            if not parent_data:
                continue
            if 'children' not in parent_data:
                parent_data['children'] = []
            parent_data['children'].append(data)

        return NodeAdapter.from_neo4j(nodes[root_uuid])

        # node_data = nodes[root_uuid]
        # root_node = Node(
        #     uuid=node_data['uuid'],
        #     level=node_data['level'],
        #     content=node_data['content'],
        #     children=[]
        # )
        #
        # temp_nodes = {
        #     uuid: Node(uuid=uuid, level=data['level'], content=data['content'], children=[])
        #     for uuid, data in nodes.items()
        # }
        #
        # for uuid, node in temp_nodes.items():
        #     if node.uuid == root_uuid:
        #         continue
        #
        #     # add the node to its parent
        #     temp_nodes[node_data['parent_uuid']].children.append(node)
        #
        # # Find and sort child nodes by their ordinal value
        # child_nodes = [
        #     NodeAdapter.build_hierarchy(child_uuid, nodes)
        #     for child_uuid, child_data in nodes.items()
        #     if child_data.get('parent_uuid') == root_uuid
        # ]
        # root_node.children = sorted(child_nodes, key=lambda x: nodes[x.uuid]['ordinal'])
        #
        # return root_node

    @staticmethod
    def to_chromadb(node: Node):
        return {
            'id': node.uuid,
            'document': node.content,
            'metadata': {'level': node.level}
        }
