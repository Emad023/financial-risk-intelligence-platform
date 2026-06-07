from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
import numpy as np

MODEL_NAME = "BAAI/bge-small-en-v1.5"

model = SentenceTransformer(MODEL_NAME)

INPUT_DIR = Path("data/chunks")
OUTPUT_DIR = Path("data/embeddings")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for chunk_file in INPUT_DIR.glob("*_chunks.json"):

    print(f"Processing {chunk_file.name}")

    chunks = json.loads(
        chunk_file.read_text(encoding="utf-8")
    )

    embeddings = model.encode(
        chunks,
        show_progress_bar=True
    )

    output_file = OUTPUT_DIR / f"{chunk_file.stem}.npz"

    np.savez_compressed(
        output_file,
        embeddings=embeddings,
        chunks=chunks
    )

    print(f"Saved: {output_file}")