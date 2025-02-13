import os

class OpenSearchUtils:
    @staticmethod
    def opensearch_config():
        opensearch_endpoint = os.getenv("OPENSEARCH_ENDPOINT")
        configured = bool(opensearch_endpoint)  # True if string is not empty/None, otherwise False.
        return {"configured": configured}