import os
from datetime import datetime

def log_llm_call(tag: str, prompt: str, response: str, error: str, output_dir: str):
    log_path = os.path.join(output_dir, "llm_raw.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n=== {tag} | {datetime.now().isoformat()} ===\n")
        f.write("PROMPT:\n" + prompt + "\n\n")
        f.write("RESPONSE:\n" + response + "\n")
        if error:
            f.write("ERROR:\n" + error + "\n")
