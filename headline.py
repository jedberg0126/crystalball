def generate_headline(label: str, name: str) -> str:
    if label == "LIKELY":
        return f"LIKELY: {name}"
    if label == "TRENDING":
        return f"TRENDING: {name}?"
    raise ValueError("Invalid label")
