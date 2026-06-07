from sentence_transformers import SentenceTransformer

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)

from src.search.document_store import (
    load_all_chunks
)

from src.search.bm25_search import (
    bm25_search
)

from src.rag.comparison_detector import (
    extract_companies
)

from src.search.reranker import (
    rerank_results
)

COLLECTION_NAME = "financial_reports"

embedding_model = None


def get_embedding_model():

    global embedding_model

    if embedding_model is None:

        print(
            "Loading Embedding Model..."
        )

        embedding_model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    return embedding_model

# =====================================
# Company Detection
# =====================================

def detect_company(question):

    question = question.lower()

    companies = {
        "apple": "apple",
        "microsoft": "microsoft",
        "nvidia": "nvidia",
        "tesla": "tesla"
    }

    for company in companies:

        if company in question:
            return companies[company]

    return None


# =====================================
# Hybrid Search
# =====================================

def hybrid_search(
    question,
    top_k=5,
    forced_company=None
):

    company = (
        forced_company
        if forced_company
        else detect_company(question)
    )

    from src.vector_db.qdrant_client import (
        client as qdrant
    )

    query_embedding = get_embedding_model().encode(
        question,
        normalize_embeddings=True
    )

    # ==========================
    # Vector Search
    # ==========================

    if company:

        vector_results = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding.tolist(),
            limit=15,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="company",
                        match=MatchValue(
                            value=company
                        )
                    )
                ]
            )
        )

    else:

        vector_results = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding.tolist(),
            limit=15
        )

    candidate_chunks = []

    seen = set()

    # ==========================
    # Vector Results
    # ==========================

    for point in getattr(
        vector_results,
        "points",
        []
    ):

        key = (
            point.payload["document"],
            point.payload["chunk_id"]
        )

        if key in seen:
            continue

        seen.add(key)

        chunk = (
            f"[Source: {point.payload['document']} | Chunk {point.payload['chunk_id']}]\n\n"
            f"{point.payload['text']}"
        )

        candidate_chunks.append(
            {
                "text": chunk,
                "source": {
                    "company": point.payload["company"],
                    "document": point.payload["document"],
                    "chunk_id": point.payload["chunk_id"]
                }
            }
        )

    # ==========================
    # BM25 Search
    # ==========================

    all_docs = load_all_chunks()

    if company:

        all_docs = [
            doc
            for doc in all_docs
            if doc["company"] == company
        ]

    bm25_results = bm25_search(
        question,
        [doc["text"] for doc in all_docs],
        top_k=15
    )

    # ==========================
    # BM25 Results
    # ==========================

    for text, score in bm25_results:

        matching_doc = next(
            (
                doc
                for doc in all_docs
                if doc["text"] == text
            ),
            None
        )

        if matching_doc is None:
            continue

        key = (
            matching_doc["document"],
            matching_doc["chunk_id"]
        )

        if key in seen:
            continue

        seen.add(key)

        chunk = (
            f"[Company: {matching_doc['company']}]\n"
            f"[Document: {matching_doc['document']}]\n"
            f"[Chunk ID: {matching_doc['chunk_id']}]\n\n"
            f"{matching_doc['text']}"
        )

        candidate_chunks.append(
            {
                "text": chunk,
                "source": {
                    "company": matching_doc["company"],
                    "document": matching_doc["document"],
                    "chunk_id": matching_doc["chunk_id"]
                }
            }
        )

    # ==========================
    # Reranking
    # ==========================

    if not candidate_chunks:
        return "", []

    reranked_chunks = rerank_results(
        question,
        candidate_chunks,
        top_k=top_k
    )

    # ==========================
    # Build Final Context
    # ==========================

    chunks = []
    sources = []

    for item in reranked_chunks:

        chunks.append(
            item["text"]
        )

        sources.append(
            item["source"]
        )

    context = "\n\n".join(
        chunks
    )

    return context, sources
# =====================================
# Comparison Search
# =====================================

def comparison_search(
    question,
    top_k=5
):

    companies = extract_companies(
        question
    )

    if len(companies) < 2:

        return hybrid_search(
            question,
            top_k=top_k
        )

    all_context = []

    all_sources = []

    seen_sources = set()

    for company in companies:

        context, sources = hybrid_search(
            question,
            top_k=top_k,
            forced_company=company
        )

        all_context.append(
            context
        )

        for source in sources:

            key = (
                source["document"],
                source["chunk_id"]
            )

            if key in seen_sources:
                continue

            seen_sources.add(key)

            all_sources.append(
                source
            )

    final_context = "\n\n".join(
        all_context
    )

    return (
        final_context,
        all_sources
    )

