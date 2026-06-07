import re


def extract_business_section(text: str) -> str:

    patterns = [
        r"ITEM\s*1\.?\s*BUSINESS",
        r"Item\s*1\.?\s*Business",
        r"ITEM\s*1\s*BUSINESS",
        r"Item\s*1\s*Business",
    ]

    start_pos = None

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            start_pos = match.start()
            break

    if start_pos is not None:
        return text[start_pos:]

    return text


def clean_text(text: str) -> str:

    text = re.sub(
        r".*Form\s+10-K.*?\|\s*\d+",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^\s*\d+\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    text = extract_business_section(text)

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    text = "\n".join(
        line.strip()
        for line in text.splitlines()
    )

    return text.strip()