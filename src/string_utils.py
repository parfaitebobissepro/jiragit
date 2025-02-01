import unicodedata

def remove_accents(input_str):
    """Remove accents from a string."""
    normalized_str = unicodedata.normalize("NFD", input_str)
    return "".join(c for c in normalized_str if unicodedata.category(c) != "Mn")