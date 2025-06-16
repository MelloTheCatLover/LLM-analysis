import os
import subprocess
import json

def classify_with_llm(text: str, categories: list[str], llm_model: str, output_dir: str) -> tuple[str, str]:
    """
    Классификация документа: использует LLM, возвращает (category, description).
    Логирует промпт и ответ в output_dir/llm_raw.log.
    """
    prompt = f"""
Ты — помощник приёмной комиссии. Определи, к какой категории относится текст документа.
Ответь строго в формате:
Категория: <одна из категорий>
Описание: <одно предложение>

Категории:
{os.linesep.join(f"- {c}" for c in categories)}

Текст документа (первые 2000 символов):
{text[:2000]}
""".strip()

    print("Отправка запроса к LLM...")
    proc = subprocess.run(
        ['ollama', 'run', llm_model],
        input=prompt.encode('utf-8'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output = proc.stdout.decode('utf-8', errors='ignore').strip()
    err = proc.stderr.decode('utf-8', errors='ignore').strip()

    log_path = os.path.join(output_dir, 'llm_raw.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as log:
            log.write('\n\n=== Новый вызов classify_with_llm ===\n')
            log.write(prompt + '\n\n')
            log.write("Ответ:\n" + output + '\n')
            if err:
                log.write("Stderr:\n" + err + '\n')
            log.write('=======================\n')
    except Exception as e:
        print(f"Ошибка записи лога LLM: {e}")

    print("\nОтвет LLM (classify):")
    print(output)

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


def analyze_document(text: str, category: str, llm_model: str, output_dir: str) -> dict:
    """
    Глубокий анализ содержимого документа в зависимости от категории.
    Формирует специальный промпт для извлечения структурированных данных и комментариев.
    Возвращает словарь с результатами анализа: либо разобранные поля, либо сырый текст анализа.
    Логируется в output_dir/llm_raw.log.
    """
    if category == "Диплом бакалавра/специалиста":
        prompt_body = """
Документ считается дипломом бакалавра/специалиста.
Извлеки из приведённого текста следующие поля:
- ФИО выпускника (если есть)
- Название учебного заведения
- Квалификация/степень (бакалавр/специалист)
- Направление подготовки
- Дата выдачи
- Регистрационный номер (если указан)
- Наличие упоминания Государственной аттестационной комиссии или аналогичного органа
Верни JSON с ключами:
{
  "name": "",
  "institution": "",
  "qualification": "",
  "major": "",
  "issue_date": "",
  "reg_number": "",
  "has_gak": false,
  "comment": ""
}
Если какое-то поле не найдено, укажи его как пустую строку или false.
Дай развёрнутый комментарий в поле "comment" о качестве и полноте диплома.
""".strip()
    elif category == "Приложение к диплому":
        prompt_body = """
Документ считается приложением к диплому (таблица с оценками, дисциплинами и т.д.).
Извлеки из текста:
- Список дисциплин и оценок (формат: [{"discipline": "", "grade": ""}])
- Общее количество дисциплин
- Наличие информации об итоговой квалификационной работе
- Общее количество зачётных единиц или часов (если указано)
Верни JSON:
{
  "courses": [],
  "total_courses": 0,
  "has_final_work": false,
  "total_credits": "",
  "comment": ""
}
Если поле отсутствует — оставь пустым или false.
""".strip()
    elif category == "Список научных публикаций":
        prompt_body = """
Документ считается списком научных публикаций.
Извлеки все публикации в формате:
- название статьи
- журнал/конференция
- год
- DOI или URL (если есть)
Верни JSON:
{
  "publications": [
    {
      "title": "",
      "venue": "",
      "year": "",
      "doi": ""
    }
  ],
  "total_publications": 0,
  "comment": ""
}
""".strip()
    elif category == "Подтверждение индексации публикаций":
        prompt_body = """
Документ считается подтверждением индексации публикаций (скриншот или текст из Scopus/WoS и т.п.).
Извлеки:
- Упомянутые журналы или статьи, указание Q-класса (Q1/Q2 и т.п.)
- Общее число проиндексированных статей, если есть
Верни JSON:
{
  "indexed_items": [
    {
      "title": "",
      "journal": "",
      "index_rank": ""
    }
  ],
  "total_indexed": 0,
  "comment": ""
}
""".strip()
    elif category == "Сертификат участника конференции":
        prompt_body = """
Документ считается сертификатом участника конференции (или дипломом за выступление).
Извлеки:
- Название конференции
- Дата проведения
- Роль (участник/докладчик/секретарь и т.п.)
- Тема доклада (если указано)
Верни JSON:
{
  "conference": "",
  "date": "",
  "role": "",
  "talk_title": "",
  "comment": ""
}
""".strip()
    elif category == "Тезисы доклада":
        prompt_body = """
Документ считается тезисами доклада.
Извлеки:
- Название доклада/тезисов
- Название конференции/сборника
- Год
- Ключевые слова (если есть)
Верни JSON:
{
  "title": "",
  "venue": "",
  "year": "",
  "keywords": [],
  "comment": ""
}
""".strip()
    elif category == "Диплом победителя олимпиад/конкурсов":
        prompt_body = """
Документ считается дипломом/грамотой победителя или призёра олимпиады/конкурса.
Извлеки:
- Название мероприятия
- Дата
- Место (1-е/2-е/3-е или др.)
- Уровень (школьный/региональный/всероссийский/международный)
Верни JSON:
{
  "event": "",
  "date": "",
  "place": "",
  "level": "",
  "comment": ""
}
""".strip()
    elif category == "Сертификат о прохождении курса/стажировки":
        prompt_body = """
Документ считается сертификатом о прохождении курса или стажировки.
Извлеки:
- Название курса/организатора
- Дата начала и окончания (если указано)
- Объём (часы/кредиты)
Верни JSON:
{
  "course": "",
  "provider": "",
  "start_date": "",
  "end_date": "",
  "duration": "",
  "comment": ""
}
""".strip()
    elif category == "Сертификат IELTS/TOEFL":
        prompt_body = """
Документ считается сертификатом IELTS или TOEFL.
Извлеки:
- Тип теста (IELTS/TOEFL)
- Баллы/оценки по секциям
- Дата теста
Верни JSON:
{
  "test_type": "",
  "scores": { "listening": "", "reading": "", "writing": "", "speaking": "" },
  "date": "",
  "comment": ""
}
""".strip()
    elif category in ["Патент", "Акт о внедрении", "Подтверждение участия в гранте"]:
        prompt_body = """
Документ относится к научно-исследовательской работе (патент/акт о внедрении/участие в гранте).
Извлеки ключевую информацию:
- Для патента: название изобретения, номер патента, дату, заявителя.
- Для акта о внедрении: название организации, описание внедрения, дату.
- Для участия в гранте: название гранта, роль заявителя, период.
Верни JSON:
{
  "info": { },
  "comment": ""
}
""".strip()
    elif category in ["Справка о педагогическом стаже", "Рабочая программа курса", "Учебное пособие"]:
        prompt_body = """
Документ относится к педагогической деятельности.
Извлеки:
- Для справки о стаже: организация, период работы, должность.
- Для рабочей программы: название курса, цели, содержание, объем.
- Для учебного пособия: название, ISBN (если есть), авторы.
Верни JSON:
{
  "info": { },
  "comment": ""
}
""".strip()
    elif category in ["Грамота / благодарность", "Диплом спортивного соревнования"]:
        prompt_body = """
Документ относится к общественной или спортивной деятельности.
Извлеки:
- Название мероприятия или организации, причину благодарности/соревнования.
- Дата.
- Роль или достижение (волонтер/участник/место).
Верни JSON:
{
  "info": { },
  "comment": ""
}
""".strip()
    elif category == "Заявление темы магистерской диссертации":
        prompt_body = """
Документ — заявление темы магистерской диссертации.
Извлеки:
- ФИО студента
- Тема диссертации
- Научный руководитель (если указан)
- Дата подачи
Верни JSON:
{
  "student_name": "",
  "thesis_topic": "",
  "supervisor": "",
  "date": "",
  "comment": ""
}
""".strip()
    else:
        prompt_body = f"""
Документ отнесён к категории "{category}".
Дай краткий анализ содержимого: извлеки ключевые элементы, важные поля, и дай комментарий о формате и полноте информации.
Верни JSON:
{{ 
  "summary": "", 
  "comment": "" 
}}
""".strip()

    prompt = prompt_body + "\n\nТекст документа (до 2000 символов):\n" + text[:2000]

    print("Отправка запроса к LLM для глубокого анализа...")
    proc = subprocess.run(
        ['ollama', 'run', llm_model],
        input=prompt.encode('utf-8'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output = proc.stdout.decode('utf-8', errors='ignore').strip()
    err = proc.stderr.decode('utf-8', errors='ignore').strip()

    log_path = os.path.join(output_dir, 'llm_raw.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as log:
            log.write('\n\n=== Новый вызов analyze_document ===\n')
            log.write(f"Category: {category}\n")
            log.write(prompt + '\n\n')
            log.write("Ответ:\n" + output + '\n')
            if err:
                log.write("Stderr:\n" + err + '\n')
            log.write('=======================\n')
    except Exception as e:
        print(f"Ошибка записи лога LLM (analyze_document): {e}")

    analysis = {}
    try:
        start = output.find('{')
        end = output.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = output[start:end+1]
            analysis = json.loads(json_str)
        else:
            analysis = {"raw": output}
    except Exception as e:
        print(f"Ошибка парсинга JSON из ответа LLM: {e}")
        analysis = {"raw": output}

    return analysis
