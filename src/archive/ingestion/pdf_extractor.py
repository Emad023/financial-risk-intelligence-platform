from pathlib import Path
import fitz

RAW_DIR = Path("data/raw/filings")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for pdf_file in RAW_DIR.glob("*.pdf"):

    print(f"Processing {pdf_file.name}")

    doc = fitz.open(pdf_file)

    text = ""

    for page in doc:
        text += page.get_text()

    output_file = OUTPUT_DIR / f"{pdf_file.stem}.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved {output_file}")