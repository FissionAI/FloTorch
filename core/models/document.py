import uuid
from dataclasses import dataclass, field
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError


@dataclass
class Document:
    """
    A class representing a document to be stored in DynamoDB.
    """
    index: str
    execution_id: str
    chunk_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    child_text: str = ""
    parent_id: str = ""
    embedding: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dynamodb_table_name: str = "Documents"

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans the input text by removing quotes, special symbols, extra whitespaces,
        newline (\n), and tab (\t) characters.
        """
        import re

        text = re.sub(r'[^a-zA-Z0-9\s]', '', text.replace('"', '').replace("'", ""))
        text = re.sub(r'\s+', ' ', text.replace('\n', ' ').replace('\t', ' ')).strip()
        return text

    def save_to_dynamodb(self) -> bool:
        """
        Saves the current document to a DynamoDB table.
        """
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(self.dynamodb_table_name)

        try:
            table.put_item(Item=self.to_dict())
            return True
        except ClientError as e:
            print(f"Failed to save document to DynamoDB: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Document object to a dictionary.
        """
        return {
            "_index": self.index,
            "execution_id": self.execution_id,
            "chunk_id": self.chunk_id,
            "text": self.text,
            "child_text": self.child_text,
            "parent_id": self.parent_id,
            "embedding": self.embedding,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """
        Creates a Document object from a dictionary.
        """
        return cls(
            index=data["_index"],
            execution_id=data["execution_id"],
            chunk_id=data.get("chunk_id", str(uuid.uuid4())),
            text=data.get("text", ""),
            child_text=data.get("child_text", ""),
            parent_id=data.get("parent_id", ""),
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def get_from_dynamodb(cls, chunk_id: str, table_name: str) -> "Document":
        """
        Retrieves a document from DynamoDB using the chunk ID.
        """
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)

        try:
            response = table.get_item(Key={"chunk_id": chunk_id})
            if "Item" in response:
                return cls.from_dict(response["Item"])
            else:
                raise ValueError(f"No document found with chunk_id: {chunk_id}")
        except ClientError as e:
            print(f"Failed to retrieve document from DynamoDB: {e}")
            raise
