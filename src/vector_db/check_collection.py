from qdrant_client import QdrantClient

COLLECTION_NAME = "financial_reports"


def main():

    client = QdrantClient(path="data/qdrant")

    try:

        info = client.get_collection(
            collection_name=COLLECTION_NAME
        )

        print("\nCollection Information")
        print("-" * 40)

        print(
            f"Points Count: {info.points_count}"
        )

    finally:
        client.close()


if __name__ == "__main__":
    main()