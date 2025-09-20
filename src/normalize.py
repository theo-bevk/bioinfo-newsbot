import re
from rapidfuzz import fuzz

def clean_title(t: str) -> str:
    # Cleans up the title; only single whitespaces + removes bracketed sections
    t = re.sub(r"\s+", " ", t or "").strip()
    t = re.sub(r"\[[^]]*preprint[^]]*\]", "", t, flags=re.I)
    return t

def near_duplicate(a: str, b: str) -> bool:
    # Title similarity threshold; splits strings into tokens and compares them
    return fuzz.token_set_ratio(a, b) >= 92
