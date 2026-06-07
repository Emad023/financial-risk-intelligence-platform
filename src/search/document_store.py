from src.vector_db.qdrant_client import (
    client
)

COLLECTION_NAME = "financial_reports"


def load_all_chunks():

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=10000,
        with_payload=True
    )

    chunks = []

    for point in points:

        chunks.append(
            {
                "text":
                    point.payload["text"],
                "company":
                    point.payload["company"],
                "document":
                    point.payload["document"],
                "chunk_id":
                    point.payload["chunk_id"]
            }
        )

    return chunks