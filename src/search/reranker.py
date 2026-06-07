from sentence_transformers import CrossEncoder

reranker = None


def get_reranker():

    global reranker

    if reranker is None:

        print(
            "Loading CrossEncoder..."
        )

        reranker = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    return reranker


def rerank_results(
    question,
    chunks,
    top_k=5
):

    if not chunks:
        return []

    model = get_reranker()

    pairs = [
        (question, chunk["text"])
        for chunk in chunks
    ]

    scores = model.predict(
        pairs
    )

    ranked = sorted(
        zip(chunks, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        item[0]
        for item in ranked[:top_k]
    ]