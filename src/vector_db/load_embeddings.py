from pathlib import Path
import numpy as np

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

COLLECTION_NAME = "financial_reports"
EMBEDDING_DIR = Path("data/embeddings")


def main():

    client = QdrantClient(path="data/qdrant")

    try:

        point_id = 0

        for file in EMBEDDING_DIR.glob("*.npz"):

            print(f"\nLoading {file.name}")

            data = np.load(
                file,
                allow_pickle=True
            )

            embeddings = data["embeddings"]
            chunks = data["chunks"]

            company = file.stem.split("_")[0]

            points = []

            for vector, chunk in zip(embeddings, chunks):

                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector.tolist(),
                        payload={
                            "company": company,
                            "document": file.stem,
                            "chunk_id": point_id,
                            "text": str(chunk)
                        }
                    )
                )

                point_id += 1

            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )

            print(
                f"Inserted {len(points)} points"
            )

        print(
            f"\nFinished loading {point_id} total vectors."
        )

    finally:
        client.close()


if __name__ == "__main__":
    main()