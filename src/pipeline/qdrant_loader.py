from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

COLLECTION_NAME = "financial_reports"

def document_exists(
    client,
    document_name
):

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=10000,
        with_payload=True
    )

    for point in points:

        if (
            point.payload.get("document")
            == document_name
        ):
            return True

    return False

def upload_to_qdrant(
    chunks,
    embeddings,
    company,
    document_name
):

    from src.vector_db.qdrant_client import (
        client as qdrant
    )

    collection_info = client.get_collection(
        COLLECTION_NAME
    )

    if document_exists(
        client,
        document_name
    ):

        return {
            "status": "exists",
            "message": (
                f"{document_name} "
                "already exists in database."
            )
        }

    current_count = (
        collection_info.points_count
        or 0
    )

    points = []

    for idx, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        point_id = current_count + idx

        points.append(
            PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload={
                    "company": company.lower(),
                    "document": document_name,
                    "chunk_id": point_id,
                    "text": chunk
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return {
        "status": "inserted",
        "count": len(points)
    }
