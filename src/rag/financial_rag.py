import sys
from pathlib import Path
import re


project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.search.hybrid_search import (
    hybrid_search,
    comparison_search
)

from src.rag.comparison_detector import (
    is_comparison_question,
    extract_companies
)

from openai import OpenAI
from dotenv import load_dotenv

import os

# =====================================
# Load Environment Variables
# =====================================

load_dotenv()

# =====================================
# Configuration
# =====================================

LLM_MODEL = (
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
)

# =====================================
# OpenRouter Client
# =====================================

llm = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# =====================================
# Generate Answer
# =====================================

def generate_answer(question):

    comparison_mode = is_comparison_question(
        question
    )

    if comparison_mode:

        context, sources = comparison_search(
            question
        )

        companies = extract_companies(
            question
        )

        company_sections = ""

        for company in companies:

            company_sections += (
                f"\n{company.title()} Analysis\n"
            )

        prompt = f"""
You are a senior financial analyst.

Compare the companies using ONLY the provided context.

Context:
{context}

Question:
{question}

Provide your answer using EXACTLY these section titles:

Executive Summary

{company_sections}

Key Differences

Risk Comparison

Conclusion

Include supporting citations using:

Example:
[Source: apple_10k_2024 | Chunk 1830]

Only use citations that already exist in the provided context.

Only cite sources present in the context.

Do NOT use:
- #
- ##
- ###
- markdown tables
- footnotes
- source numbers
"""

    else:

        context, sources = hybrid_search(
            question
        )

        prompt = f"""
        You are an expert financial analyst.

        Use ONLY the provided context.

        Context:
        {context}

        Question:
        {question}

        Provide your answer using EXACTLY these section titles:

        Executive Summary

        Key Findings

        - Every finding MUST start with "- "
        - Every finding MUST include a citation.

        Example:

        - Supply chain concentration creates operational risk.
        [Source: apple_10k_2024 | Chunk 1830]

        Risk Assessment

        - Every risk MUST start with "- "
        - Every risk MUST include a citation.
        - One risk per bullet point.
        - Use only risks explicitly supported by the context.

        Example:

        - Trade restrictions could increase costs.
        [Source: apple_10k_2024 | Chunk 1845]

        Conclusion

        Keep the conclusion to 2-4 sentences.

        IMPORTANT:

        - Use ONLY citations already present in the context.
        - Never create a citation.
        - Never invent chunk numbers.
        - Never invent document names.
        - If a statement is unsupported, do not include it.

        Do NOT use:

        - #
        - ##
        - ###
        - markdown tables
        - footnotes
        """

    print("\n" + "=" * 80)
    print("LATEST VERSION OF FINANCIAL_RAG.PY LOADED")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("RETRIEVED CONTEXT")
    print("=" * 80)

    print(context[:3000])

    print("\n" + "=" * 80)
    print("RETRIEVAL METRICS")
    print("=" * 80)

    print(
        f"Sources Retrieved: {len(sources)}"
    )

    if not sources:

        return (
            "No relevant information was found in the knowledge base.",
            []
        )

    response = llm.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content":
                """

            You are a senior financial analyst.

            Analyze:

            - SEC filings
            - Risk disclosures
            - Annual reports
            - Business reports
            - Financial statements

            Rules:

            1. Use ONLY supplied context.
            2. Do NOT invent facts.
            3. If information is unavailable, explicitly state it.
            4. Return clean professional business-report text.
            5. Do NOT generate markdown tables.
            6. Do NOT generate source numbers.

            IMPORTANT:

            This platform focuses on risk intelligence.

            For non-comparison questions, generate:

            - Executive Summary
            - Key Findings
            - Risk Assessment
            - Conclusion

            Do not generate opportunities unless the user explicitly asks for them.

            IMPORTANT OUTPUT RULES:

            - Use markdown bullet points for Key Findings.
            - Use markdown bullet points for Risk Assessment.
            - Do not write Key Findings as paragraphs.
            - Do not write Risk Assessment as paragraphs.
            - One risk per bullet point.
            - Do not speculate.
            - Do not invent facts.
            - Do not generate opportunities.

            IMPORTANT CITATION RULES:

            - Every finding must include a source citation.
            - Every risk must include a source citation.
            - Use only source tags that already exist in the context.
            - Never generate fake citations.
            - Never generate unsupported statements.

            """ 

            
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = (
        response
        .choices[0]
        .message
        .content
    )


    answer = re.sub(
        r"Executive Summary\s*\n\s*-",
        "Executive Summary\n",
        answer,
        flags=re.IGNORECASE
    )

    answer = re.sub(
        r"【[^】]*】",
        "",
        answer
    )

    answer = re.sub(
        r"([a-z])([A-Z])",
        r"\1 \2",
        answer
    )

    answer = re.sub(
        r"\n{3,}",
        "\n\n",
        answer
    )

    sections = [
        "Executive Summary",
        "Key Findings",
        "Risk Assessment",
        "Conclusion",
        "Apple Analysis",
        "Tesla Analysis",
        "Microsoft Analysis",
        "NVIDIA Analysis",
        "Key Differences",
        "Risk Comparison"
    ]

    for section in sections:

        answer = re.sub(
            rf"^\s*{re.escape(section)}\s*:?\s*$",
            f"### {section}",
            answer,
            flags=re.MULTILINE
        )

    return answer, sources
# =====================================
# Public Function For Streamlit
# =====================================

def ask_financial_question(question):

    answer, sources = (
        generate_answer(
            question
        )
    )

    return answer, sources


# =====================================
# CLI Mode
# =====================================

def main():

    question = input(
        "\nAsk a Financial Question: "
    )

    answer, sources = (
        ask_financial_question(
            question
        )
    )

    print("\n")
    print("=" * 100)
    print("ANSWER")
    print("=" * 100)

    print(answer)

    print("\n")
    print("=" * 100)
    print("SOURCES")
    print("=" * 100)

    for i, source in enumerate(
        sources,
        start=1
    ):

        print(
            f"{i}. "
            f"{source['document']} "
            f"(Chunk {source['chunk_id']})"
        )


if __name__ == "__main__":

    main()