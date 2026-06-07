from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)

COLLECTION_NAME = "financial_reports"


def get_documents():

    from src.vector_db.qdrant_client import (
        client
    )

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=10000,
        with_payload=True
    )

    documents = {}

    for point in points:

        company = point.payload.get(
            "company",
            "unknown"
        )

        document = point.payload.get(
            "document",
            "unknown"
        )

        key = (
            company,
            document
        )

        if key not in documents:
            documents[key] = 0

        documents[key] += 1

    rows = []

    for (
        company,
        document
    ), count in documents.items():

        rows.append(
            {
                "Company": company,
                "Document": document,
                "Chunks": count
            }
        )

    return rows



def delete_document(
    document_name
):

    from src.vector_db.qdrant_client import (
        client
    )

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document",
                    match=MatchValue(
                        value=document_name
                    )
                )
            ]
        )
    )

    return True
