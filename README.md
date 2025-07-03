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
Windows: https://github.com/UB-Mannheim/tesseract/wiki

```

The latest installers can be downloaded here:

tesseract-ocr-w64-setup-5.5.0.20241111.exe (64 bit)

Пример файла, который нужно будет скачать

Запомните деректорию, куда устанавливаете. По умолчанию это

```
C:\Program Files\Tesseract-OCR
```

Добавьте этот путь в переменные среды: PATH

Проверьте работу командой

```
tesseract
```

_Желаемый вывод_

```
Usage:
  tesseract --help | --help-extra | --version
  tesseract --list-langs
  tesseract imagename outputbase [options...] [configfile...]

OCR options:
  -l LANG[+LANG]        Specify language(s) used for OCR.
NOTE: These options must occur before any configfile.

Single options:
  --help                Show this help message.
  --help-extra          Show extra help for advanced users.
  --version             Show version information.
  --list-langs          List available languages for tesseract engine.
```

Добавьте распозначание русского языка:

Скачайте языковой пакет с репозитория

```
https://github.com/tesseract-ocr/tessdata
```

Для русского языка:
**rus.traineddata**

Переместите его в папку:

```
C:\Program Files\Tesseract-OCR\tessdata
```

Проверьте добавление языка

```
tesseract --list-langs
```

5. Установите poppler (для pdf2image):

```
Windows: https://github.com/oschwartz10612/poppler-windows?tab=readme-ov-file

```

Скачайте архив и распакуйте в удобной дериктории, запомните путь установки и добавьте его в PATH.

Добавьте в переменные среды PATH путь до bin папки, например:

```
C:\Program Files\poppler-24.08.0\Library\bin
```

6. Установите и настройте Ollama:

Скачайте ollama c официального сайта

```
https://ollama.com/download
```

Затем загрузите модель, например:

```
ollama pull mistral
```

Тип: Текстовая LLM (7B параметров)
Разработчик: Mistral AI
Особенности:

Оптимизирована для английского и французского, но понимает другие языки (включая русский).

Хорошо справляется с генерацией текста, анализом и вопросами.

Быстрая и эффективная, работает даже на слабом железе.

или

```
ollama pull deepseek-r1:1.5b
```

Тип: Текстовая LLM (1.5B параметров)
Разработчик: DeepSeek
Особенности:

Компактная модель (1.5 млрд параметров), но с хорошей производительностью.

Поддержка английского и китайского, но может работать с русским (хуже, чем Mistral).

Экономит ресурсы, подходит для тестов и простых задач.

# Конфигурация

1. Пример config/tesseract_config.json:

Тут стандартный путь загрузки.

Также используемые языки. Использует для распознавания текста с изображений

```
{
"tesseract_cmd": "C:/Program Files/Tesseract-OCR/tesseract.exe",
"lang": "rus+eng"
}
```

2. Пример config/user_manifest.json:

Заявленные пользователем файлы и их категории.

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

# Запуск и использование

## Основной запуск

Для пакетной обработки портфолио по манифесту:

```bash
python -m src.main
```

- Обрабатывает все документы, указанные в `config/user_manifest.json`.
- Результаты сохраняются в `data/output/` (Excel, JSON, логи).

## CLI-интерфейс

Для гибкой работы с отдельными файлами и портфелями используйте CLI:

### Общая справка

```bash
python -m src.cli --help
```

### Доступные команды

#### 1. Классификация документа

```bash
python -m src.cli classify data/input/document.pdf
```

- Извлекает текст, классифицирует с помощью LLM, выводит категорию и описание.

#### 2. Глубокий анализ документа

```bash
python -m src.cli analyze data/input/document.pdf
```

- Классифицирует и анализирует документ, выводит расширенную сводку.

#### 3. Извлечение имени

```bash
python -m src.cli extract-name data/input/document.pdf --expected-name "Иван Иванов"
```

- Извлекает имя из документа, сравнивает с ожидаемым (если указано).

#### 4. Проверка соответствия категории

```bash
python -m src.cli check-match data/input/document.pdf "Диплом бакалавра"
```

- Сравнивает заявленную и определённую LLM категорию, выводит степень совпадения.

#### 5. Анализ портфолио по манифесту

```bash
python -m src.cli portfolio config/user_manifest.json
```

- Обрабатывает все документы из манифеста:
  - OCR, классификация, сравнение категорий
  - Извлечение имён (если указаны)
  - Глубокий анализ
  - Генерирует Excel и JSON отчёты с деталями, баллами, комментариями

### Примеры использования

```bash
# Классифицировать документ
python -m src.cli classify data/input/1.pdf

# Извлечь имя с проверкой
python -m src.cli extract-name data/input/1.pdf --expected-name "Петров И.И."

# Проверить соответствие категории
python -m src.cli check-match data/input/1.pdf "Диплом бакалавра"

# Обработать всё портфолио
python -m src.cli portfolio config/user_manifest.json
```

## Ожидаемый результат

- В `data/output/` появятся:
  - `details.xlsx` — подробный отчёт по каждому файлу и разделу
  - `summary.json` — структура с оценками и комментариями
  - `llm_raw.log` — лог всех LLM-запросов и ответов

### Пример вывода в терминале

```
[INFO] Processing: 1.pdf
[RESULT] LLM detected category: Диплом бакалавра
[RESULT] Category match: YES
...
[INFO] Processing: 2.pdf
[WARNING] No text extracted from 2.pdf
...
[INFO] Portfolio Analysis Complete:
[INFO] Reports saved:
   - Excel: data/output/portfolio_report_20240601_153000.xlsx
   - JSON: data/output/portfolio_summary_20240601_153000.json
```
