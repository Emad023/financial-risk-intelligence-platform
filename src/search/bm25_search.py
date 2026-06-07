from rank_bm25 import BM25Okapi
import re


def bm25_search(
    query,
    documents,
    top_k=5
):

    tokenized_docs = [

        re.findall(
            r"\b\w+\b",
            doc.lower()
        )

        for doc in documents
    ]

    bm25 = BM25Okapi(
        tokenized_docs
    )

    tokenized_query = re.findall(
        r"\b\w+\b",
        query.lower()
    )

    scores = bm25.get_scores(
        tokenized_query
    )

    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]