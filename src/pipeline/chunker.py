from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)


def create_chunks(text):

    chunks = splitter.split_text(text)

    return chunks