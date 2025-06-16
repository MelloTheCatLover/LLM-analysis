import os
import json
import pandas as pd

from ocr_processor import extract_text
from llm_client import classify_with_llm, analyze_document
from classifier import compute_similarity, is_match
from analyze_portfolio import analyze_portfolio

INPUT_DIR = 'data/input'
OUTPUT_DIR = 'data/output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open('config/tesseract_config.json', encoding='utf-8') as f:
    t_cfg = json.load(f)
TESSERACT_LANG = t_cfg.get('lang', 'rus+eng')

with open('config/categories.json', encoding='utf-8') as f:
    CATEGORIES = json.load(f)

with open('config/user_manifest.json', encoding='utf-8') as f:
    manifest = json.load(f)

LLM_MODEL = 'mistral'  # или другая модель

def main():
    detailed_docs = []

    for entry in manifest:
        fname = entry.get('filename')
        claimed = entry.get('claimed_type', '').strip()
        path = os.path.join(INPUT_DIR, fname)

        if not os.path.isfile(path):
            print(f"Ошибка: файл не найден: {path}")
            continue

        print(f"\n=== Обработка файла: {fname} ===")
        text = extract_text(path, TESSERACT_LANG)

        detected, description = classify_with_llm(text, CATEGORIES, LLM_MODEL, OUTPUT_DIR)
        sim = compute_similarity(detected, claimed)
        match = is_match(detected, claimed)

        match_str = "Да" if match else "Нет"
        print(f"Заявлено: {claimed}")
        print(f"Определено: {detected}")
        print(f"Сходство категорий (TF-IDF): {sim:.2f}")
        print(f"Совпадает с заявленным: {match_str}")

        analysis = analyze_document(text, detected, LLM_MODEL, OUTPUT_DIR)
        detailed_docs.append({
            'filename': fname,
            'claimed': claimed,
            'detected': detected,
            'description': description,
            'similarity': sim,
            'match': match,
            'text': text,
            'analysis': analysis
        })

    # Общий анализ портфолио
    summary = analyze_portfolio(detailed_docs)

    # Составляем детальную таблицу
    df_details = pd.DataFrame([
        {
            'Файл': doc['filename'],
            'Заявлено': doc['claimed'],
            'Определено': doc['detected'],
            'Описание': doc['description'],
            'Сходство': f"{doc['similarity']:.2f}",
            'Совпадает': "Да" if doc['match'] else "Нет",
            'Анализ LLM (comment)': (
                doc['analysis'].get('comment')
                if isinstance(doc['analysis'], dict) and 'comment' in doc['analysis']
                else (
                    doc['analysis'].get('raw')
                    if isinstance(doc['analysis'], dict) and 'raw' in doc['analysis']
                    else ''
                )
            )
        }
        for doc in detailed_docs
    ])

    # Сохраняем сводный JSON
    summary_path = os.path.join(OUTPUT_DIR, 'portfolio_summary.json')
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"Сводный анализ сохранён в: {summary_path}")
    except Exception as e:
        print(f"Ошибка при сохранении сводного анализа в JSON: {e}")

    # Сохраняем отчёт в Excel
    excel_path = os.path.join(OUTPUT_DIR, 'portfolio_report.xlsx')
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Лист с деталями по файлам
            df_details.to_excel(writer, sheet_name='Details', index=False)

            # Лист с оценками по разделам
            df_scores = pd.DataFrame([
                {'Раздел': sec, 'Баллы': info['score'], 'Макс': info['max']}
                for sec, info in summary.get('scores', {}).items()
            ])
            df_scores.to_excel(writer, sheet_name='Scores', index=False)

            # Лист с комментариями
            comments_df = pd.DataFrame({'Комментарии': summary.get('comments', [])})
            comments_df.to_excel(writer, sheet_name='Comments', index=False)

            # Лист с общей оценкой
            overall_df = pd.DataFrame([{
                'TotalScore': summary.get('total_score'),
                'MaxScore': summary.get('max_score'),
                'Percent': summary.get('percent'),
                'Overall': summary.get('overall_assessment')
            }])
            overall_df.to_excel(writer, sheet_name='Summary', index=False)

        print(f"Полный отчёт сохранён в Excel: {excel_path}")
    except Exception as e:
        print(f"Ошибка при сохранении Excel: {e}")
        csv_path = os.path.join(OUTPUT_DIR, 'details.csv')
        try:
            df_details.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"Детали сохранены в CSV: {csv_path}")
        except Exception as e2:
            print(f"Ошибка при сохранении CSV: {e2}")

if __name__ == '__main__':
    main()
