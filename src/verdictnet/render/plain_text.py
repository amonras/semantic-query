from models.node import Node
from render.node_renderer import NodeRenderer


class PlainTextRenderer(NodeRenderer):
    @staticmethod
    def render(node: Node, level: int = 0) -> str:
        """
        Render a node as plain text with indentation to indicate hierarchy.

        Args:
            node (Node): The node to render.
            level (int): The current depth in the hierarchy.

        Returns:
            str: The rendered plain text representation.
        """
        indent = "  " * level
        text = f"{indent}{node.content}\n"
        for child in node.children:
            text += PlainTextRenderer.render(child, level + 1)
        return text
