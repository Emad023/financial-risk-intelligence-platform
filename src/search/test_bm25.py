import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.search.document_store import (
    load_all_chunks
)

from src.search.bm25_search import (
    bm25_search
)

docs = load_all_chunks()

texts = [
    doc["text"]
    for doc in docs
]

results = bm25_search(
    "Tesla manufacturing risks",
    texts,
    top_k=5
)

for i, result in enumerate(results):

    print(f"\nResult {i+1}")

    print(result[0][:500])