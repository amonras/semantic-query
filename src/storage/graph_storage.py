import configparser
import logging
from textwrap import dedent
from typing import Optional, List, Dict

import numpy as np
import typing_extensions as te
from neo4j import Driver, GraphDatabase

import config
from models.node import Node
from storage.adapters import NodeAdapter

logger = config.logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GraphStorage:
    def __init__(self, graph_driver: Driver):
        """
        Initialize the GraphStorage with a Neo4j driver.
        """
        self.driver = graph_driver
        self._ensure_constraints()

    def _ensure_constraints(self):
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Node) REQUIRE n.uuid IS UNIQUE")

    def create_node(self, node: Node):
        """
        Create a single node in the Neo4j database.
        """
        node_data = NodeAdapter.to_neo4j(node)
        with self.driver.session() as session:
            query = """
            MERGE (n:Node {uuid: $uuid})
            SET n.level = $level, n.content = $content
            RETURN n
            """
            session.run(query, **node_data)

    def create_relationship(self, parent_uuid: str, child_uuid: str):
        with self.driver.session() as session:
            query = """
            MATCH (p:Node {uuid: $parent_uuid})
            MATCH (c:Node {uuid: $child_uuid})
            MERGE (p)-[:HAS_CHILD]->(c)
            """
            session.run(query, parent_uuid=parent_uuid, child_uuid=child_uuid)

    def store(self, root_node: Node):
        """
        Recursively store a Node and all its children in the Neo4j database.
        """
        # Create the root node
        self.create_node(root_node)

        # Recursively create child nodes and relationships
        for child in root_node.children:
            self.store(child)  # Store the child node recursively
            self.create_relationship(root_node.uuid, child.uuid)

    def batch_store(self, node_list: List[Node], parent_uuid: Optional[str] = None, ordered = False):
        """
        Batch insert nodes and relationships into Neo4j.
        If parent_uuid is provided, all the nodes will be inserted as children of the parent node.
        If ordered is True, the nodes will be inserted in as and ordered set. If children already exist for the
        parent_uuid, the new nodes will be appended to the end.
        """
        nodes = []
        relationships = []

        insert_query = dedent(
            """
                MERGE (n:Node {uuid: $uuid})
                SET n.level = $level, n.content = $content, n.ordinal = $ordinal
            """
        )
        for node in node_list:
            nd, rel = NodeAdapter.to_neo4j_with_relationships(node)
            nodes.extend(nd)
            relationships.extend(rel)

            if parent_uuid:
                relationships.append((parent_uuid, node.uuid))

        with self.driver.session() as session:
            # Insert all nodes
            for node in nodes:
                result = session.run(insert_query, **node)
                result.to_eager_result()

            # Insert all relationships
            for parent_uuid, child_uuid in relationships:
                session.run("""
                    MATCH (p:Node {uuid: $parent_uuid})
                    MATCH (c:Node {uuid: $child_uuid})
                    MERGE (p)-[:HAS_CHILD]->(c)
                """, parent_uuid=parent_uuid, child_uuid=child_uuid)

    def delete_hierarchy(self, root_uuid: str):
        """
        Delete a Node hierarchy from Neo4j by root UUID.
        """
        with self.driver.session() as session:
            query = """
            MATCH (n:Node {uuid: $root_uuid})-[:HAS_CHILD*0..]->(child)
            DETACH DELETE n, child
            """
            session.run(query, root_uuid=root_uuid)

    def delete_all(self):
        """
        Clear all nodes and relationships from the Neo4j database.
        """
        with self.driver.session() as session:
            session.run("MATCH (n:Node) DETACH DELETE n")

    def retrieve_parent(self, uuid: str, depth: int = np.inf) -> Node:
        """
        Retrieve the parent of a node and all its children.

        Args:
            uuid (str): The UUID of the node to retrieve the parent of.

        Returns:
            Node: The parent node.
        """

        if depth < np.inf:
            raise NotImplementedError("Depth limit not implemented")

        with self.driver.session() as session:
            # Query to fetch all nodes and their relationships in the hierarchy
            query = dedent("""
            MATCH (n:Node {uuid: $uuid})<-[:HAS_CHILD]-(parent)
            RETURN parent.uuid AS parent_uuid;
            """)

            logger.debug(f"Querying parent for {uuid}")
            logger.debug(f"Query: \n{query}")

            result = session.run(query, uuid=uuid).single()

            if not result:
                return None

            parent_uuid = result['parent_uuid']

            return self.retrieve_hierarchy(parent_uuid)

    def retrieve_hierarchy(self, root_uuid: str, depth: int = np.inf) -> Node:
        """
        Retrieve a node and all its children as a hierarchy.

        Args:
            root_uuid (str): The UUID of the root node to retrieve.
            depth (int): The maximum depth to retrieve.

        Returns:
            Node: The root node with all its children populated.
        """

        if depth < np.inf:
            raise NotImplementedError("Depth limit not implemented yet")

        with self.driver.session() as session:
            # Query to fetch all nodes and their relationships in the hierarchy
            query = dedent("""
            MATCH (n:Node {uuid: $root_uuid})-[:HAS_CHILD*0..]->(child)
            OPTIONAL MATCH (child)<-[:HAS_CHILD]-(parent)
            RETURN n.uuid AS root_uuid, 
                   n.level AS root_level, 
                   n.content AS root_content, 
                   collect({parent: parent.uuid, self: child.uuid, contents: child.content, level: child.level, order:child.ordinal}) AS relationships;
            """)
            logger.debug(f"Querying hierarchy for {root_uuid}")
            logger.debug(f"Query: \n{query}")

            result = session.run(query, root_uuid=root_uuid).single()

            if not result:
                return None

            # Parse the result to reconstruct the hierarchy
            nodes = {}
            root_node_data = {
                'uuid': result['root_uuid'],
                'level': result['root_level'],
                'content': result['root_content'],
                'parent_uuid': None,
            }
            nodes[root_uuid] = root_node_data

            # Process children
            for relationship in result['relationships']:
                nodes[relationship['self']] = {
                    'uuid': relationship['self'],
                    'level': relationship['level'],
                    'content': relationship['contents'],
                    'ordinal': relationship['order'],
                    'parent_uuid': relationship['parent'],
                }

            # Build the hierarchy
            return NodeAdapter.build_hierarchy(root_uuid, nodes)

    # def retrieve_hierarchies(self, root_uuids: List[str]) -> Dict[str, Node]:
    #     """
    #     Retrieve multiple node hierarchies from Neo4j by root UUIDs.
    #
    #     Args:
    #         root_uuids (List[str]): The UUIDs of the root nodes to retrieve.
    #
    #     Returns:
    #         Dict[str, Node]: A dictionary of root nodes with all their children populated.
    #     """
    #     with self.driver.session() as session:

    # TODO: There seems to be a bug with this query. Fix it.

    #         query = """
    #         UNWIND $root_uuids AS root_uuid
    #         MATCH (n:Node {uuid: root_uuid})-[:HAS_CHILD*0..]->(child)
    #         OPTIONAL MATCH (child)<-[:HAS_CHILD]-(parent)
    #         WHERE parent.uuid <> child.uuid
    #         RETURN root_uuid,
    #                n.uuid AS node_uuid,
    #                n.level AS node_level,
    #                n.content AS node_content,
    #                collect(child.uuid) AS child_uuids,
    #                collect(child.level) AS child_levels,
    #                collect(child.content) AS child_contents,
    #                collect(child.ordinal) AS child_order,
    #                collect(parent.uuid) AS parent_uuids
    #         """
    #         result = session.run(query, root_uuids=root_uuids)
    #
    #         nodes = {}
    #         for record in result:
    #             root_uuid = record['root_uuid']
    #             if root_uuid not in nodes:
    #                 nodes[root_uuid] = {}
    #
    #             node_data = {
    #                 'uuid': record['node_uuid'],
    #                 'level': record['node_level'],
    #                 'content': record['node_content'],
    #                 'parent_uuid': None,
    #             }
    #             nodes[root_uuid][record['node_uuid']] = node_data
    #
    #             child_uuids = record['child_uuids']
    #             child_levels = record['child_levels']
    #             child_contents = record['child_contents']
    #             child_order = record['child_order']
    #             parent_uuids = record['parent_uuids']
    #
    #             assert len(child_uuids) == len(child_levels)
    #             assert len(child_uuids) == len(child_contents)
    #             assert len(child_uuids) == len(child_order)
    #             # assert len(child_uuids) == len(parent_uuids)
    #
    #             for child_uuid, level, content, ordinal, parent_uuid in zip(
    #                     child_uuids, child_levels, child_contents, child_order, parent_uuids
    #             ):
    #                 nodes[root_uuid][child_uuid] = {
    #                     'uuid': child_uuid,
    #                     'level': level,
    #                     'content': content,
    #                     'ordinal': ordinal,
    #                     'parent_uuid': parent_uuid,
    #                 }
    #
    #         hierarchies = {}
    #         for root_uuid in root_uuids:
    #             if root_uuid in nodes:
    #                 hierarchies[root_uuid] = NodeAdapter.build_hierarchy(root_uuid, nodes[root_uuid])
    #
    #         return hierarchies

    def retrieve_by(self, level: Optional[str] = None, content: Optional[str] = None) -> List[Node]:
        """
        Retrieve nodes by their level.

        Args:
            level (str): The level of the nodes to retrieve.
            content (str): The content of the nodes to retrieve

        Returns:
            List[Node]: A list of nodes at the specified level.
        """
        with self.driver.session() as session:
            clauses = []
            kwargs = {}
            if level is not None:
                clauses.append("level: $level")
                kwargs['level'] = level
            if content is not None:
                clauses.append("content: $content")
                kwargs['content'] = content

            query = dedent(f"""
                MATCH 
                    (n:Node {{ {','.join(clauses)} }}) 
                RETURN 
                    n.uuid AS uuid, 
                    n.level AS level, 
                    n.content AS content
            """)

            result = session.run(query, **kwargs)

            uuids = [record['uuid'] for record in result]

            nodes = [self.retrieve_hierarchy(uuid) for uuid in uuids]

            return nodes

    @classmethod
    def get_graph_storage(cls, conf: Optional[configparser.ConfigParser] = None) -> 'GraphStorage':
        conf = conf or config.get_config()

        neo4j_driver = GraphDatabase.driver(conf['neo4j']['url'],
                                            auth=(conf['neo4j']['user'], conf['neo4j']['password']))
        graph_storage = GraphStorage(neo4j_driver)

        return graph_storage
