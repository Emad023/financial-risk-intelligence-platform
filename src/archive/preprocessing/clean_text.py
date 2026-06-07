from pathlib import Path
import re

INPUT_DIR = Path("data/processed")
OUTPUT_DIR = Path("data/cleaned")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_business_section(text: str) -> str:
    """
    Find the first occurrence of Item 1 Business
    regardless of capitalization or spacing.
    """

    patterns = [
        r"ITEM\s*1\.?\s*BUSINESS",
        r"Item\s*1\.?\s*Business",
        r"ITEM\s*1\s*BUSINESS",
        r"Item\s*1\s*Business",
    ]

    start_pos = None

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            start_pos = match.start()
            print(f"Found business section using pattern: {pattern}")
            break

    if start_pos is not None:
        return text[start_pos:]

    print("WARNING: Could not find Item 1 Business section")
    return text


def clean_text(text: str) -> str:

    # Remove page headers such as:
    # Apple Inc. | 2024 Form 10-K | 15
    text = re.sub(
        r".*Form\s+10-K.*?\|\s*\d+",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove standalone page numbers
    text = re.sub(
        r"^\s*\d+\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    # Keep only from Item 1 Business onward
    text = extract_business_section(text)

    # Remove repeated spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # Strip whitespace on each line
    text = "\n".join(
        line.strip()
        for line in text.splitlines()
    )

    return text.strip()


def main():

    txt_files = list(INPUT_DIR.glob("*.txt"))

    print(f"Found {len(txt_files)} files")

    for txt_file in txt_files:

        print(f"\nCleaning: {txt_file.name}")

        text = txt_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        cleaned_text = clean_text(text)

        output_file = OUTPUT_DIR / txt_file.name

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(cleaned_text)

        print(f"Saved: {output_file}")
        print(f"Original Length: {len(text):,}")
        print(f"Cleaned Length: {len(cleaned_text):,}")


if __name__ == "__main__":
    main()