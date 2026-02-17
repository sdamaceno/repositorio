from __future__ import annotations

import re
import unicodedata

STOPWORDS = {
    "de",
    "da",
    "do",
    "dos",
    "das",
    "para",
    "com",
    "e",
}


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [t for t in text.split() if t and t not in STOPWORDS]
    return " ".join(tokens)
