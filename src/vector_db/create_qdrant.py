from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

COLLECTION_NAME = "financial_reports"


def main():

    client = QdrantClient(path="data/qdrant")

    try:

        collections = client.get_collections()

        existing_collections = [
            collection.name
            for collection in collections.collections
        ]

        if COLLECTION_NAME not in existing_collections:

            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )

            print(f"Collection '{COLLECTION_NAME}' created successfully.")

        else:
            print(f"Collection '{COLLECTION_NAME}' already exists.")

    finally:
        client.close()


if __name__ == "__main__":
    main()