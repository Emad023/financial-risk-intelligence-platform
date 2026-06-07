from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

MODEL_NAME = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "financial_reports"

model = SentenceTransformer(MODEL_NAME)


def search(query, company=None, top_k=5):

    client = QdrantClient(path="data/qdrant")

    try:

        print("\nGenerating query embedding...")

        query_embedding = model.encode(
            query,
            normalize_embeddings=True
        )

        search_filter = None

        if company:

            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="company",
                        match=MatchValue(
                            value=company.lower()
                        )
                    )
                ]
            )

        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding.tolist(),
            limit=top_k,
            query_filter=search_filter
        )

        print("\n" + "=" * 100)
        print("QUESTION:")
        print(query)
        print("=" * 100)

        if company:
            print(f"\nCompany Filter: {company}")

        for i, point in enumerate(results.points, start=1):

            print("\n" + "-" * 100)

            print(f"Result #{i}")

            print(
                f"Company: {point.payload.get('company')}"
            )

            print(
                f"Similarity Score: {round(point.score, 4)}"
            )

            print("-" * 100)

            text = point.payload.get("text", "")

            print(text[:1200])

            print("\n")

    finally:
        client.close()


def main():

    print("\nFinancial Intelligence Search Engine")
    print("=" * 50)

    query = input(
        "\nEnter Question: "
    )

    company_filter = input(
        "\nCompany Filter (apple/microsoft/nvidia or press Enter): "
    ).strip()

    if company_filter == "":
        company_filter = None

    search(
        query=query,
        company=company_filter,
        top_k=5
    )


if __name__ == "__main__":
    main()