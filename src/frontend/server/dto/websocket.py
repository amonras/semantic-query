from dataclasses import dataclass
from typing import List


class WebSocketMessage:
    """
    Base class for WebSocket messages. It provides a way to serialize and deserialize messages.
    """
    def to_dict(self):
        # It serializes the object to a dictionary. The type key determines the type of message, and
        # the payload key contains the message data.
        return {"type": self.__class__.__name__, "payload": self.__dict__}

    @classmethod
    def from_dict(cls, data):
        # It deserializes a dictionary to the right subclass of WebSocketMessage according to the type key.
        class_name = data["type"]
        class_payload = data["payload"]
        class_type = globals()[class_name]
        return class_type(**class_payload)


@dataclass
class ConnectionId(WebSocketMessage):
    """
    A message to send the connection id to the client.
    """
    connection_id: str


@dataclass
class FileUploaded(WebSocketMessage):
    """
    A message to send the file uploaded to the client.
    """
    filename: str


@dataclass
class ChatQueryMessage(WebSocketMessage):
    """
    A query chat message to send to the client.
    """
    message: str


@dataclass
class ChatResponseMessage(WebSocketMessage):
    """
    A response chat message to send to the client.
    """
    message: str


@dataclass
class DisplayDocuments(WebSocketMessage):
    """
    A message to send the documents to the client.
    """
    documents: List[str]
