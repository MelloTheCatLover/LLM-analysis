import os
import json
# import subprocess  # No longer needed
from src.core.logger import log_llm_call

def extract_person_name(text: str, expected_name: str = "", model: str = "deepseek-r1:1.5b", output_dir: str = "data/output") -> dict:
    """
    Checks if the expected_name exists in the text. Returns a dict with keys:
    - full_name: the expected_name if found, else empty string
    - match_with_expected: True if found, else False
    - comment: explanation
    """
    if not expected_name:
        return {"full_name": "", "match_with_expected": False, "comment": "Ожидаемое имя не указано"}
    found = expected_name in text
    return {
        "full_name": expected_name if found else "",
        "match_with_expected": found,
        "comment": "Имя найдено в тексте" if found else "Имя не найдено в тексте"
    }
