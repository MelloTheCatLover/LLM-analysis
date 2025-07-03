import os
import json
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("data/output/app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

from src.core.config_loader import load_json
from src.core.models import DocumentResult
from src.processors.ocr import extract_text
from src.processors.classifier import compute_similarity, is_match
from src.processors.llm_client import classify_with_llm
from src.processors.name_extractor import extract_person_name
from src.processors.portfolio_analyzer import analyze_portfolio

# Загрузка конфигов
TESSERACT_CFG = load_json("config/tesseract_config.json")
LLM_CFG       = load_json("config/llm_config.json")
CATEGORIES    = load_json("config/categories.json")
MANIFEST      = load_json("config/user_manifest.json")

LLM_MODEL = LLM_CFG.get("model", "mistral")

INPUT_DIR  = "data/input"
OUTPUT_DIR = "data/output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def main() -> None:
    """Main entry point for portfolio analysis. Processes documents, extracts information, and generates reports."""
    if not MANIFEST or not isinstance(MANIFEST, list) or "expected_name" not in MANIFEST[0]:
        logging.critical("Manifest must start with an object containing 'expected_name'")
        return
    expected_name = MANIFEST[0]["expected_name"].strip()
    documents = MANIFEST[1:]
    results = []
    for entry in documents:
        fname = entry["filename"]
        claimed = entry.get("claimed_type", "").strip()
        path = os.path.join(INPUT_DIR, fname)
        if not os.path.isfile(path):
            logging.error(f"File not found: {path}")
            continue
        logging.info(f"Processing document: {fname}")
        logging.info(f"Claimed category: {claimed if claimed else 'Not provided'}")
        # 1. Извлечение текста
        logging.info(f"Extracting text from file: {fname}")
        text = extract_text(path, TESSERACT_CFG["lang"])
        if not text.strip():
            logging.warning(f"No text extracted from {fname}")
            continue
        # 2. Классификация
        logging.info(f"Running LLM classification for: {fname}")
        detected, desc, llm_raw = classify_with_llm(text, CATEGORIES, LLM_MODEL, OUTPUT_DIR)
        logging.debug("[LLM RAW OUTPUT] ------------------------------")
        logging.debug(llm_raw)
        logging.debug("[END LLM RAW OUTPUT] --------------------------")
        logging.info(f"LLM detected category: {detected}")
        logging.info(f"LLM description: {desc}")
        sim = compute_similarity(detected, claimed)
        match = is_match(detected, claimed)
        logging.info(f"Similarity score: {sim:.3f}")
        logging.info(f"Category match: {'YES' if match else 'NO'}")
        # 3. Проверка ФИО
        logging.info(f"Extracting person name from: {fname}")
        person = extract_person_name(text, expected_name, LLM_MODEL, OUTPUT_DIR)
        full_name = person.get('full_name', 'Not found')
        fio_match = person.get('match_with_expected', False)
        comment = person.get('comment', '')
        logging.info(f"Extracted name: {full_name}")
        logging.info(f"Name matches expected: {'YES' if fio_match else 'NO'}")
        if comment:
            logging.info(f"Name extraction comment: {comment}")
        # 4. Глубокий анализ только если ФИО совпало
        analysis = {}
        if fio_match:
            logging.info(f"Running deep analysis for: {fname}")
            analysis = {"category": detected}
        else:
            logging.info(f"Skipping deep analysis for {fname} (FIO mismatch)")
        results.append({
            "filename": fname,
            "claimed": claimed,
            "detected": detected,
            "description": desc,
            "similarity": sim,
            "match": match,
            "text": text,
            "person": person,
            "fio_match": fio_match,
            "analysis": analysis
        })
    logging.info("Running portfolio analysis and generating reports...")
    filtered_results = [r for r in results if r["fio_match"]]
    summary = analyze_portfolio(filtered_results)
    df = pd.DataFrame([{
        "Файл":   r["filename"],
        "Заявлено": r["claimed"],
        "Определено": r["detected"],
        "Описание": r["description"],
        "Сходство": f"{r['similarity']:.2f}",
        "Совпадает": "Да" if r["match"] else "Нет",
        "ФИО": r["person"].get("full_name", ""),
        "ФИО совпадает": "Да" if r["fio_match"] else "Нет",
        "Комментарий ФИО": r["person"].get("comment", ""),
        "Анализ": json.dumps(r["analysis"], ensure_ascii=False) if r["fio_match"] else ""
    } for r in results])
    details_path = os.path.join(OUTPUT_DIR, "details.xlsx")
    summary_path = os.path.join(OUTPUT_DIR, "summary.json")
    df.to_excel(details_path, index=False)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    logging.info(f"Reports saved: {details_path}, {summary_path}")
    logging.info("Portfolio analysis complete. See output directory for details.")

if __name__ == "__main__":
    main()
