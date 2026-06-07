from qdrant_client import QdrantClient

client = QdrantClient(
    path="data/qdrant",
    force_disable_check_same_thread=True
)