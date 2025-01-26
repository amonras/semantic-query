from models.node import Node


class NodeRenderer:
    @staticmethod
    def render(node: Node):
        """
        Render a node. Should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")
