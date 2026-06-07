from sentence_transformers import (
    SentenceTransformer
)

MODEL_NAME = "BAAI/bge-small-en-v1.5"

model = SentenceTransformer(
    MODEL_NAME
)


def generate_embeddings(chunks):

    embeddings = model.encode(
        chunks,
        show_progress_bar=False
    )

    return embeddings