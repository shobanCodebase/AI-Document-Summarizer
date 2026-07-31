def chunk_text(text: str, max_chars: int = 8000) -> list[str]:
    paragraphs = text.split("\n")
    chunks = [""]

    for paragraph in paragraphs:
        if not paragraph.strip():
            continue  # skip empty lines entirely

        if len(chunks[-1]) + len(paragraph) < max_chars:
            chunks[-1] += paragraph + "\n"
        else:
            chunks.append(paragraph + "\n")

    # Remove the empty placeholder chunk if nothing was ever added to it
    chunks = [c for c in chunks if c.strip()]

    return chunks