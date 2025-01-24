from models.node import Node
from storage.adapters import NodeAdapter


def test_to_neo4j_with_relationships_single_node():
    node = Node(level="root", content="Root Node")
    nodes, relationships = NodeAdapter.to_neo4j_with_relationships(node)
    assert len(nodes) == 1
    assert nodes[0]['uuid'] == node.uuid
    assert relationships == []


def test_to_neo4j_with_relationships_with_children():
    root = Node(level="root", content="Root", children=[
        Node(level="child", content="Child 1"),
        Node(level="child", content="Child 2")
    ])
    nodes, relationships = NodeAdapter.to_neo4j_with_relationships(root)
    assert len(nodes) == 3  # Root + 2 children
    assert len(relationships) == 2  # Root -> Child 1, Root -> Child 2
    assert relationships == [(root.uuid, root.children[0].uuid), (root.uuid, root.children[1].uuid)]
    assert [node['ordinal'] for node in nodes] == [None, 0, 1]


def test_to_neo4j_with_relationships_deep_hierarchy():
    root = Node(level="root", content="Root", children=[
        Node(level="child", content="Child", children=[
            Node(level="grandchild", content="Grandchild")
        ])
    ])
    nodes, relationships = NodeAdapter.to_neo4j_with_relationships(root)
    assert len(nodes) == 3  # Root, Child, Grandchild
    assert len(relationships) == 2  # Root -> Child, Child -> Grandchild


def test_build_hierarchy():
    nodes = {
        "root-uuid": {"uuid": "root-uuid", "level": "root", "content": "Root Node", 'ordinal': 0},
        "child-uuid": {"uuid": "child-uuid", "level": "child", "content": "Child Node", "parent_uuid": "root-uuid",
                       'ordinal': 0},
    }
    root_node = NodeAdapter.build_hierarchy("root-uuid", nodes)

    assert root_node.uuid == "root-uuid"
    assert len(root_node.children) == 1
    assert root_node.children[0].uuid == "child-uuid"


def test_build_hierarchy_with_reversed_children():
    # Prepare nodes dictionary with children in reverse order
    nodes = {
        "root-uuid": {"uuid": "root-uuid", "level": "root", "content": "Root Node"},
        "child2-uuid": {"uuid": "child2-uuid", "level": "child", "content": "Child Node 2", "parent_uuid": "root-uuid",
                        "ordinal": 1},
        "child1-uuid": {"uuid": "child1-uuid", "level": "child", "content": "Child Node 1", "parent_uuid": "root-uuid",
                        "ordinal": 0},
    }

    # Call _build_hierarchy
    root_node = NodeAdapter.build_hierarchy("root-uuid", nodes)

    # Assert root node properties
    assert root_node.uuid == "root-uuid"
    assert root_node.level == "root"
    assert root_node.content == "Root Node"

    # Assert children are reconstructed in the correct order
    assert len(root_node.children) == 2
    assert root_node.children[0].uuid == "child1-uuid"  # Ensure child1 comes first
    assert root_node.children[0].content == "Child Node 1"
    assert root_node.children[1].uuid == "child2-uuid"  # Ensure child2 comes second
    assert root_node.children[1].content == "Child Node 2"


def test_build_hierarchy_with_deep_structure():
    nodes = {
        "root-uuid": {"uuid": "root-uuid", "level": "root", "content": "Root Node", 'ordinal': 0},
        "child-uuid": {"uuid": "child-uuid", "level": "child", "content": "Child Node", "parent_uuid": "root-uuid",
                       'ordinal': 0},
        "grandchild-uuid": {"uuid": "grandchild-uuid", "level": "grandchild", "content": "Grandchild Node",
                            "parent_uuid": "child-uuid", 'ordinal': 0},
    }
    root_node = NodeAdapter.build_hierarchy("root-uuid", nodes)

    assert root_node.uuid == "root-uuid"
    assert len(root_node.children) == 1
    assert root_node.children[0].uuid == "child-uuid"
    assert len(root_node.children[0].children) == 1
    assert root_node.children[0].children[0].uuid == "grandchild-uuid"
    assert len(root_node.children[0].children[0].children) == 0
    assert root_node.children[0].children[0].content == "Grandchild Node"
    assert root_node.children[0].children[0].level == "grandchild"


def test_from_neo4j():
    # Create a nested dictionary with Node data and an extra field "ordinal"
    node_data = {
        'uuid': 'root-uuid',
        'level': 'root',
        'content': 'Root Node',
        'children': [
            {
                'uuid': 'child-uuid-1',
                'level': 'child',
                'content': 'Child Node 1',
                'ordinal': 1,
                'children': []
            },
            {
                'uuid': 'child-uuid-2',
                'level': 'child',
                'content': 'Child Node 2',
                'ordinal': 0,
                'children': []
            }
        ]
    }

    # Call the from_neo4j method
    root_node = NodeAdapter.from_neo4j(node_data)

    # Assertions
    assert root_node.uuid == 'root-uuid'
    assert root_node.level == 'root'
    assert root_node.content == 'Root Node'
    assert len(root_node.children) == 2
    assert root_node.children[0].uuid == 'child-uuid-2'  # Ordered by ordinal
    assert root_node.children[1].uuid == 'child-uuid-1'
    assert root_node.children[0].content == 'Child Node 2'
    assert root_node.children[1].content == 'Child Node 1'
