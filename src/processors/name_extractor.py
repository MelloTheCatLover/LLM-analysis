import os
import json
import subprocess
from src.core.logger import log_llm_call

def extract_person_name(text: str, expected_name: str = "", model: str = "deepseek-r1:1.5b", output_dir: str = "data/output") -> dict:
    prompt = (
        "Ты — эксперт по анализу документов. Определи ФИО человека в документе.\n"
        "Ответи JSON:\n"
        '{ "full_name": "", "match_with_expected": true/false, "comment": "" }\n\n'
        "Текст (до 2000):\n" + text[:2000] +
        f"\n\nОжидаемое ФИО: {expected_name or '<не указано>'}"
    )
    proc = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out = proc.stdout.decode("utf-8", errors="ignore")
    err = proc.stderr.decode("utf-8", errors="ignore")
    log_llm_call("extract_person_name", prompt, out, err, output_dir)

    try:
        js = out[out.find("{"):out.rfind("}")+1]
        return json.loads(js)
    except Exception:
        return {"raw": out}
