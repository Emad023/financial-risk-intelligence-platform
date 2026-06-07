import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import tempfile
import os
from sentence_transformers import CrossEncoder


@st.cache_resource
def load_reranker():

    return CrossEncoder(
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )

@st.cache_resource
def load_embedding_model():

    return SentenceTransformer(
        "BAAI/bge-small-en-v1.5"
    )

# =====================================
# Fix Imports FIRST
# =====================================

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# =====================================
# Project Imports
# =====================================

from src.rag.financial_rag import (
    ask_financial_question
)

from src.pipeline.process_document import (
    process_document
)

from src.vector_db.document_manager import (
    get_documents,
    delete_document
)

from src.reporting.pdf_report import (
    generate_pdf_report
)

# =====================================
# Page Config
# =====================================

st.set_page_config(
    page_title="Financial Risk Intelligence Platform",
    page_icon="📈",
    layout="wide"
)

# =====================================
# Sidebar
# =====================================

with st.sidebar:

    st.sidebar.markdown("""
    ### AI Pipeline

    Question
    ↓
    Hybrid Search
    ↓
    Vector Search (Qdrant)
    +   
    BM25 Search
    ↓
    Cross Encoder Reranker
    ↓
    LLM Analysis
    ↓
    Financial Insights
    """)

    st.title("⚙️ Settings")

    st.markdown("---")

    selected_company = st.selectbox(
        "Company",
        [
            "Auto Detect",
            "Apple",
            "Microsoft",
            "NVIDIA"
        ]
    )

    st.markdown("---")

    st.subheader("📌 Sample Questions")

    st.markdown("""
**Apple**
- What are Apple's supply chain risks?

**Microsoft**
- How is Microsoft using artificial intelligence?

**NVIDIA**
- What is NVIDIA's data center strategy?
                
**Comparison**
- Compare Apple and Tesla supply chain risks
""")

    st.markdown("---")

    st.info(
        """
        Enterprise Financial Intelligence Platform

        Powered by:
        - SEC Filings
        - Qdrant
        - BGE Embeddings
        - RAG
        - LLMs
        """
    )

    st.markdown("---")

    st.subheader("📄 Upload Financial Report")

    uploaded_file = st.file_uploader(
        "Choose PDF",
        type=["pdf"]
    )

    company_name = st.text_input(
        "Company Name",
        placeholder="e.g. tesla"
    )

    if st.button("📥 Process Document"):

        if uploaded_file is None:

            st.warning(
                "Please upload a PDF."
            )

        elif not company_name:

            st.warning(
                "Please enter company name."
            )

        else:

            temp_pdf_path = None

            try:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp:

                    tmp.write(
                        uploaded_file.read()
                    )

                    temp_pdf_path = tmp.name

                with st.spinner(
                    "Processing document..."
                ):

                    result = process_document(
                        pdf_path=temp_pdf_path,
                        company=company_name,
                        document_name=Path(
                            uploaded_file.name
                        ).stem
                    )

                if result["status"] == "exists":

                    st.warning(
                        result["message"]
                    )

                else:

                    st.success(
                        "Document processed successfully!"
                    )

                    st.json(result)

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )

            finally:

                if (
                    temp_pdf_path
                    and os.path.exists(temp_pdf_path)
                ):

                    os.remove(
                        temp_pdf_path
                    )
    st.markdown("---")

    st.subheader("📂 Loaded Documents")

    documents = get_documents()

    if documents:

        doc_df = pd.DataFrame(
            documents
        )

        st.dataframe(
            doc_df,
            width="stretch",
            hide_index=True
        )

        st.markdown("---")

        document_names = sorted(
            doc_df["Document"].unique()
        )

        selected_document = st.selectbox(
            "Select Document To Delete",
            document_names
        )

        if st.button(
            "🗑 Delete Document"
        ):

            delete_document(
                selected_document
            )

            st.success(
                f"{selected_document} deleted successfully."
            )

            st.rerun()

    else:

        st.info(
            "No documents loaded."
        )

# =====================================
# Header
# =====================================

st.title("📈 Financial Risk Intelligence Platform")

st.markdown("""
### AI-Powered Financial Analysis

Analyze SEC filings using:

- RAG (Retrieval Augmented Generation)
- Vector Search (Qdrant)
- Financial LLM Analysis
- Source Citations
""")

st.divider()

# =====================================
# Question Input
# =====================================

question = st.text_area(
    "Ask a Financial Question",
    placeholder="Example: What are Apple's supply chain risks?",
    height=120
)

# =====================================
# Analyze Button
# =====================================

if st.button(
    "🚀 Analyze",
    width="stretch"
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Analyzing financial documents..."
        ):

            try:

                answer, sources = (
                    ask_financial_question(
                        question
                    )
                )

                st.session_state["answer"] = answer
                st.session_state["sources"] = sources
                st.session_state["question"] = question

                st.session_state["analysis_complete"] = True

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )
                
# =====================================
# Display Results
# =====================================

if st.session_state.get(
    "analysis_complete",
    False
):

    answer = st.session_state["answer"]
    sources = st.session_state["sources"]

    st.success(
        "Analysis Completed"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Sources Used",
            len(sources)
        )

        with st.expander("View Sources"):

            for source in sources:

                st.markdown(
                f"""
        • **{source['document']}**
        - Chunk: {source['chunk_id']}
        - Company: {source['company']}
        """
                )

    with col2:

        companies = sorted(
            set(
                source["company"].upper()
                for source in sources
            )
        )

        if len(companies) == 1:

            st.metric(
                "Company",
                companies[0]
            )
        else:

            st.metric(
                "Companies",
                ", ".join(companies)
            )

    st.divider()

    st.subheader("📈 Retrieval Metrics")

    m1, m2, m3 = st.columns(3)

   

    with m1:
        st.metric(
            "Sources Retrieved",
            len(sources)
        )

    with m2:
        st.metric(
            "Documents Used",
            len(
                set(
                    s["document"]
                    for s in sources
                )
            )
        )
    with m3:
        st.metric(
            "Chunks Analyzed",
            len(sources)
        )

    st.subheader(
        "📊 AI Analysis"
    )

    st.markdown(answer, unsafe_allow_html=False)

    st.markdown("---")

    if st.button(
        "📄 Generate PDF Report"
    ):

        pdf_path = generate_pdf_report(
            st.session_state["question"],
            st.session_state["answer"],
            st.session_state["sources"]
        )

        st.session_state[
            "pdf_path"
        ] = pdf_path

        st.success(
            "PDF Report Generated Successfully!"
        )

    if "pdf_path" in st.session_state:

        with open(
            st.session_state["pdf_path"],
            "rb"
        ) as pdf_file:

            st.download_button(
                label="⬇ Download PDF",
                data=pdf_file.read(),
                file_name=Path(
                    st.session_state["pdf_path"]
                ).name,
                mime="application/pdf",
                width="stretch"
            )

    st.divider()

    st.subheader(
        "📚 Sources Used"
    )

    source_df = pd.DataFrame(
        sources
    )

    st.dataframe(
        source_df,
        width="stretch",
        hide_index=True
    )
                

# =====================================
# Footer
# =====================================

st.markdown("---")

st.caption(
    "AI-Powered Financial Risk Intelligence Platform"
)