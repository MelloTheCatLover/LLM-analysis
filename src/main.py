import os
import json
import fitz                                 
import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import subprocess
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────────────────────────────────────────
#  Настройки из config/
# ─────────────────────────────────────────────────────────────────────────────

with open('config/tesseract_config.json', encoding='utf-8') as f:
    t_cfg = json.load(f)
pytesseract.pytesseract.tesseract_cmd = t_cfg['tesseract_cmd']
TESSERACT_LANG = t_cfg.get('lang', 'rus+eng')

with open('config/categories.json', encoding='utf-8') as f:
    CATEGORIES = json.load(f)

INPUT_DIR  = 'data/input'
OUTPUT_DIR = 'data/output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

LLM_MODEL = 'mistral'


# ─────────────────────────────────────────────────────────────────────────────
#  OCR и извлечение текста
# ─────────────────────────────────────────────────────────────────────────────

def extract_text(filepath: str) -> str:
    """Пытаемся получить текст напрямую, иначе — через OCR."""
    try:
        doc = fitz.open(filepath)
        txt = ''.join(page.get_text() for page in doc)
        if txt.strip():
            print(f"=======Извлечение текста из PDF без OCR: {os.path.basename(filepath)}=======")
            return txt
    except Exception as e:
        print(f"=======Ошибка PyMuPDF: {e}=======")

    print(f"=======Используем OCR для: {os.path.basename(filepath)}=======")
    images = convert_from_path(filepath, dpi=300)
    ocr_text = ''
    for img in images:
        ocr_text += pytesseract.image_to_string(img, lang=TESSERACT_LANG)
    txt_path = filepath + '.ocr.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(ocr_text)
    print(f"=======OCR завершён, символов: {len(ocr_text)} (сохранено в {os.path.basename(txt_path)})=======")
    return ocr_text


# ─────────────────────────────────────────────────────────────────────────────
#  Вызов LLM и парсинг ответа
# ─────────────────────────────────────────────────────────────────────────────

def classify_with_llm(text: str) -> tuple[str, str]:
    """Отправляем промпт локальной LLM и возвращаем (category, description)."""
    prompt = f"""
Ты — помощник приёмной комиссии. Определи, к какой категории относится текст документа.  
Ответь строго в формате:
Категория: <одна из категорий>
Описание: <одно предложение>

Категории:
{os.linesep.join(f"- {c}" for c in CATEGORIES)}

Текст документа (первые 2000 символов):
{text[:2000]}
""".strip()

    print("=======Отправка запроса в LLM=======")
    proc = subprocess.run(
        ['ollama', 'run', LLM_MODEL],
        input=prompt.encode('utf-8'),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output = proc.stdout.decode('utf-8', errors='ignore').strip()

    # Логируем промпт и ответ
    with open(os.path.join(OUTPUT_DIR, 'llm_raw.log'), 'a', encoding='utf-8') as log:
        log.write('\n\n=== Новый вызов LLM ===\n')
        log.write(prompt + '\n\n')
        log.write(output + '\n')
        log.write('=======================\n')

    print("\n======= Ответ LLM:\n" + '-'*40 + f"\n{output}\n=======" + '-'*40)

    # Извлекаем категорию и описание надёжно
    category, description = 'Иное', ''
    for line in output.splitlines():
        low = line.lower()
        if 'категория' in low and ':' in line:
            parts = line.split(':', 1)
            category = parts[1].strip()
        elif 'описание' in low and ':' in line:
            parts = line.split(':', 1)
            description = parts[1].strip()

    return category, description


# ─────────────────────────────────────────────────────────────────────────────
#  Сравнение категорий
# ─────────────────────────────────────────────────────────────────────────────

def compute_similarity(a: str, b: str) -> float:
    vec = TfidfVectorizer().fit_transform([a, b])
    return float(cosine_similarity(vec[0], vec[1])[0][0])

def is_match(detected: str, claimed: str) -> bool:
    """Возвращает True, если детектированная категория близка к заявленной."""
    # векторная близость
    sim = compute_similarity(detected, claimed)
    if sim >= 0.65:
        return True
    # fallback на строковое сравнение
    return difflib.SequenceMatcher(None, detected.lower(), claimed.lower()).ratio() > 0.7


# ─────────────────────────────────────────────────────────────────────────────
#  Основной пайплайн
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # Загружаем манифест пользователя
    with open('config/user_manifest.json', encoding='utf-8') as f:
        manifest = json.load(f)

    results = []
    for entry in manifest:
        fname = entry['filename']
        claimed = entry['claimed_type']
        path = os.path.join(INPUT_DIR, fname)
        print(f"\n=== Обработка {fname} ===")
        text = extract_text(path)
        detected, desc = classify_with_llm(text)
        match = is_match(detected, claimed)
        results.append({
            'Файл': fname,
            'Заявлено': claimed,
            'Определено LLM': detected,
            'Описание LLM': desc,
            'Совпадает': '✅' if match else '❌',
            'Сходство': f"{compute_similarity(detected, claimed):.2f}"
        })

    # Сохраняем отчёт
    df = pd.DataFrame(results)
    out_xlsx = os.path.join(OUTPUT_DIR, 'report.xlsx')
    df.to_excel(out_xlsx, index=False)
    print(f"\n=======Готово! Отчёт сохранён в {out_xlsx}=======")

if __name__ == '__main__':
    main()
