import os
import subprocess
import re
from src.core.logger import log_llm_call
import logging

def classify_with_llm(text: str, categories: list[str], model: str, output_dir: str) -> tuple[str, str, str]:
    """
    Classify a document using an LLM. Returns (category, description, raw_output).
    - Uses a robust prompt with an explicit format and example.
    - Uses regex for reliable extraction.
    - Logs prompt and response.
    - Handles malformed or empty output gracefully.
    """
    prompt = (
        "Ты — помощник приёмной комиссии. Определи категорию документа.\n"
        "Ответь строго в формате:\nКатегория: <...>\nОписание: <...>\n\n"
        "Категории:\n" + "\n".join(f"- {c}" for c in categories) +
        "\n\nТекст (первые 2000 знаков):\n" + text[:2000] +
        "\n\nПример:\nКатегория: 1.1 диплом с отличием\nОписание: Диплом бакалавра с отличием\n"
    )
    proc = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out = proc.stdout.decode("utf-8", errors="ignore").strip()
    err = proc.stderr.decode("utf-8", errors="ignore").strip()
    if "no such model" in err.lower() or "not found" in err.lower():
        logging.critical(f"Ollama error: {err}")
        import sys
        sys.exit(1)
    log_llm_call("classify_with_llm", prompt, out, err, output_dir)

    # Use regex for robust parsing (регистронезависимый)
    cat_match = re.search(r"Категория:\s*(.+)", out, re.IGNORECASE)
    desc_match = re.search(r"Описание:\s*(.+)", out, re.IGNORECASE)
    category = cat_match.group(1).strip() if cat_match else "Иное"
    description = desc_match.group(1).strip() if desc_match else ""

    # Fallback for empty or malformed output
    if not out or (not cat_match and not desc_match):
        category = "Иное"
        description = ""
    return category, description, out
