from verdictnet.models.node import Node
from verdictnet.render.node_renderer import NodeRenderer


class HTMLRenderer(NodeRenderer):
    @staticmethod
    def render(node: Node, preamble='') -> str:
        """
        Render a node as HTML using <details> and <summary> tags.

        Args:
            node (Node): The node to render.
            preamble (str): Optional preamble to add before the node.

        Returns:
            str: The rendered HTML representation.

        Return a collapsable representation of the node
        """
        out = preamble
        if not node.children:
            out += f'<p id="{node.uuid}">{node.content}</p>'
        else:
            out += f"""
            <details id="{node.uuid}">
                <summary>{node.content}</summary>
                <ul>
                    {''.join([HTMLRenderer.render(child) for child in node.children])}
                </ul>
            </details>
        """

        return out
