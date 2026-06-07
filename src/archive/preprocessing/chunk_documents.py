from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json

INPUT_DIR = Path("data/cleaned")
OUTPUT_DIR = Path("data/chunks")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

for txt_file in INPUT_DIR.glob("*.txt"):

    print(f"Processing {txt_file.name}")

    text = txt_file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    chunks = splitter.split_text(text)

    output_file = OUTPUT_DIR / f"{txt_file.stem}_chunks.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    print(f"Created {len(chunks)} chunks")