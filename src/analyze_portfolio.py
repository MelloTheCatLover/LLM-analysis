from typing import List, Dict

PORTFOLIO_SECTIONS = {
    "Документы об образовании": [
        "Диплом бакалавра/специалиста",
        "Приложение к диплому"
    ],
    "Научные публикации": [
        "Список научных публикаций",
        "Подтверждение индексации публикаций"
    ],
    "Участие в конференциях": [
        "Сертификат участника конференции",
        "Тезисы доклада"
    ],
    "Олимпиады, конкурсы, доп. образование": [
        "Диплом победителя олимпиад/конкурсов",
        "Сертификат о прохождении курса/стажировки",
        "Сертификат IELTS/TOEFL"
    ],
    "Научно-исследовательская работа": [
        "Патент",
        "Акт о внедрении",
        "Подтверждение участия в гранте"
    ],
    "Педагогическая деятельность": [
        "Справка о педагогическом стаже",
        "Рабочая программа курса",
        "Учебное пособие"
    ],
    "Общественная и спортивная деятельность": [
        "Грамота / благодарность",
        "Диплом спортивного соревнования"
    ],
    "Прочее": [
        "Заявление темы магистерской диссертации",
        "Иное"
    ]
}

def analyze_portfolio(docs: List[Dict]) -> Dict:
    section_presence = {sec: [] for sec in PORTFOLIO_SECTIONS}
    comments = []
    total_score = 0
    max_score = 0

    for doc in docs:
        det = doc.get('detected', '')
        placed = False
        for section, cat_list in PORTFOLIO_SECTIONS.items():
            if det in cat_list:
                section_presence[section].append(doc)
                placed = True
                break
        if not placed:
            section_presence["Прочее"].append(doc)

    scores = {}
    for section, docs_in_sec in section_presence.items():
        if section == "Документы об образовании":
            max_sec = 2
            has_diploma = any(doc['detected'] == "Диплом бакалавра/специалиста" for doc in docs_in_sec)
            has_appendix = any(doc['detected'] == "Приложение к диплому" for doc in docs_in_sec)
            score = int(has_diploma) + int(has_appendix)
        else:
            max_sec = 1
            score = 1 if docs_in_sec else 0
        scores[section] = {'score': score, 'max': max_sec}
        total_score += score
        max_score += max_sec

    for section, info in scores.items():
        score = info['score']
        max_sec = info['max']
        docs_in_sec = section_presence[section]

        if score == 0:
            comments.append(f"[{section}] — нет предоставленных документов.")
        else:
            if max_sec > 1 and score < max_sec:
                if section == "Документы об образовании":
                    missing = []
                    if not any(doc['detected'] == "Диплом бакалавра/специалиста" for doc in docs_in_sec):
                        missing.append("диплом")
                    if not any(doc['detected'] == "Приложение к диплому" for doc in docs_in_sec):
                        missing.append("приложение к диплому")
                    comments.append(f"[{section}] — документы представлены частично: отсутствуют {', '.join(missing)}.")
                else:
                    comments.append(f"[{section}] — документы представлены частично, рекомендуется дополнение.")
            else:
                comments.append(f"[{section}] — документы представлены.")

        for doc in docs_in_sec:
            analysis = doc.get('analysis', {})
            fname = doc.get('filename')
            det = doc.get('detected')
            if isinstance(analysis, dict) and 'raw' not in analysis:
                if det == "Диплом бакалавра/специалиста":
                    missing_fields = []
                    for fld in ['institution', 'qualification', 'issue_date', 'reg_number']:
                        val = analysis.get(fld)
                        if not val:
                            missing_fields.append(fld)
                    if missing_fields:
                        comments.append(f"[{fname}] — в дипломе отсутствуют поля: {', '.join(missing_fields)}.")
                    else:
                        comments.append(f"[{fname}] — диплом содержит все ключевые поля.")
                elif det == "Приложение к диплому":
                    courses = analysis.get('courses')
                    if isinstance(courses, list):
                        if len(courses) < 3:
                            comments.append(f"[{fname}] — обнаружено мало дисциплин ({len(courses)}).")
                        else:
                            comments.append(f"[{fname}] — приложение содержит {len(courses)} дисциплин.")
                    else:
                        comments.append(f"[{fname}] — не удалось извлечь список дисциплин.")
                elif det == "Список научных публикаций":
                    pubs = analysis.get('publications')
                    if isinstance(pubs, list):
                        if len(pubs) == 0:
                            comments.append(f"[{fname}] — список публикаций пуст или не распознан.")
                        else:
                            comments.append(f"[{fname}] — количество распознанных публикаций: {len(pubs)}.")
                    else:
                        comments.append(f"[{fname}] — не удалось извлечь публикации.")
            else:
                comments.append(f"[{fname}] — структура ответа от LLM нераспознана, требуется проверка вручную.")

            text = doc.get('text', '') or ''
            if len(text.strip()) < 200:
                comments.append(f"[{fname}] — короткий распознанный текст (менее 200 символов).")

    percent = total_score / max_score * 100 if max_score > 0 else 0
    if percent >= 80:
        overall = "Портфолио оценивается как сильное."
    elif percent >= 50:
        overall = "Портфолио оценивается как среднее."
    else:
        overall = "Портфолио требует доработки."

    summary = {
        'scores': scores,
        'total_score': total_score,
        'max_score': max_score,
        'percent': round(percent, 1),
        'overall_assessment': overall,
        'comments': comments
    }
    return summary
