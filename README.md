# 📚 Система анализа портфолио поступающих

## Описание проекта

Этот проект предназначен для автоматизированного анализа портфолио поступающих на магистратуру или аспирантуру. Система выполняет следующие задачи:

- Извлекает текст из PDF-файлов (прямо или через OCR)
- Классифицирует документы по типу с помощью локальной LLM (например, Mistral, DeepSeek через Ollama)
- Сравнивает заявленную и распознанную категории
- Извлекает ключевые данные из документов (дата, вуз, оценки и т.п.)
- Формирует оценку по 8 разделам портфолио
- Генерирует Excel-отчёт и JSON-сводку

## Структура проекта

```.
├── src/ # Исходный код
│ ├── main.py # Точка входа
│ ├── ocr_processor.py # Модуль для распознавания текста
│ ├── llm_client.py # Обработка LLM-запросов
│ ├── classifier.py # Сравнение категорий
│ ├── analyze_portfolio.py # Оценка по разделам портфолио
├── config/
│ ├── categories.json # Список категорий документов
│ ├── user_manifest.json # Список файлов и заявленных типов
│ ├── tesseract_config.json # Путь до tesseract + язык
├── data/
│ ├── input/ # Входные PDF-документы
│ └── output/ # Автоматически создаётся, содержит отчёты
├── requirements.txt # Зависимости Python
└── README.md # Данный файл
```

## Установка

1. Установите Python 3.10+
2. Создайте виртуальное окружение:

```
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/macOS

```

3. Установите зависимости:

```
pip install -r requirements.txt
```

4. Установите Tesseract OCR:

```
Windows: https://github.com/tesseract-ocr/tesseract/wiki

Linux: sudo apt install tesseract-ocr
```

5. Установите poppler (для pdf2image):

```
Windows: https://blog.alivate.com.au/poppler-windows/

Linux: sudo apt install poppler-utils
```

6. Установите и настройте Ollama:

Затем загрузите модель, например:

```
ollama pull mistral
```

или

```
ollama pull deepseek:chat
```

# Конфигурация

1. Пример config/tesseract_config.json:

Тут стандартный путь загрузки.

```
{
"tesseract_cmd": "C:/Program Files/Tesseract-OCR/tesseract.exe",
"lang": "rus+eng"
}
```

2. Пример config/user_manifest.json:

```
[
  {
    "filename": "1.pdf",
    "claimed_type": "Документ, удостоверяющий получение степени бакалавра в области Информатики и Вычислительная Техника"
  },
  {
    "filename": "2.pdf",
    "claimed_type": "Диплом бакалавра"
  },
  {
    "filename": "3.pdf",
    "claimed_type": "Приложение к диплому"
  },
  {
    "filename": "4.pdf",
    "claimed_type": "Сертификат IELTS/TOEFL"
  }
]

```

# Запуск

```
python src/main.py
```

# Ожидаемый результат

## После выполнения:

В папке data/output/ будут созданы:

- `portfolio_report.xlsx` – подробный отчёт по каждому файлу и разделу

- `portfolio_summary.json` – структура с оценками и комментариями

- `llm_raw.log` – лог всех запросов и ответов LLM

## Пример вывода в терминале:

```
=== Обработка файла: 1.pdf ===
Извлечён текст из PDF без OCR: 1.pdf
Заявлено: Диплом бакалавра/специалиста; Определено: Диплом бакалавра/специалиста; Сходство: 0.98; Совпадает: ✅

=== Обработка файла: 2.pdf ===
Используем OCR для: 2.pdf
OCR завершён, символов: 1923
Заявлено: Приложение к диплому; Определено: Приложение к диплому; Сходство: 0.95; Совпадает: ✅

Формируется отчёт...
Готово! Отчёт сохранён в data/output/portfolio_report.xlsx
```

Пример оценки портфолио
В отчёте рассчитываются:

Баллы по каждому из 8 разделов

## Финальная оценка:

```
Total Score: 6 / 8
Percent: 75%
Overall: Среднее портфолио
```
