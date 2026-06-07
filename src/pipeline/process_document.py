from pathlib import Path

from src.pipeline.pdf_processor import (
    extract_text_from_pdf
)

from src.pipeline.text_cleaner import (
    clean_text
)

from src.pipeline.chunker import (
    create_chunks
)

from src.pipeline.embedder import (
    generate_embeddings
)

from src.pipeline.qdrant_loader import (
    upload_to_qdrant
)


def process_document(
    pdf_path,
    company,
    document_name=None
):

    if document_name is None:

        document_name = Path(
            pdf_path
        ).stem

    print("Extracting text...")
    raw_text = extract_text_from_pdf(
        pdf_path
    )

    print("Cleaning text...")
    cleaned_text = clean_text(
        raw_text
    )

    print("Creating chunks...")
    chunks = create_chunks(
        cleaned_text
    )

    print(
        f"Created {len(chunks)} chunks"
    )

    print("Generating embeddings...")
    embeddings = generate_embeddings(
        chunks
    )

    print("Uploading to Qdrant...")

    inserted = upload_to_qdrant(
        chunks=chunks,
        embeddings=embeddings,
        company=company,
        document_name=document_name
    )

    if inserted["status"] == "exists":

        return {
            "status": "exists",
            "message": inserted["message"]
        }

    return {
        "status": "success",
        "document": document_name,
        "company": company,
        "chunks": len(chunks),
        "vectors_uploaded": inserted["count"]
    }