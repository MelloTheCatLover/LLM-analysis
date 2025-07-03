import json
from src.processors.llm_client import classify_with_llm

def test_classify_with_llm_structure(monkeypatch):
    # Подменяем вызов subprocess для теста
    def fake_run(*args, **kwargs):
        class Result:
            stdout = "Категория: Диплом\nОписание: Документ о высшем образовании".encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    cat, desc, raw = classify_with_llm("текст", ["Диплом", "Аттестат"], "fake-model", ".")
    assert cat == "Диплом"
    assert desc.startswith("Документ")
    assert "Категория" in raw

def test_classify_with_llm_different_category(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = "Категория: Аттестат\nОписание: Документ о среднем образовании".encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    cat, desc, raw = classify_with_llm("текст", ["Диплом", "Аттестат"], "fake-model", ".")
    assert cat == "Аттестат"
    assert desc.startswith("Документ")
    assert "Аттестат" in raw

def test_classify_with_llm_no_category_found(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = "Описание: Какой-то документ".encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    cat, desc, raw = classify_with_llm("текст", ["Диплом", "Аттестат"], "fake-model", ".")
    assert cat == "Иное"
    assert desc == "Какой-то документ"  # Description is still extracted even if category is not found
    assert "Описание" in raw

def test_classify_with_llm_no_description(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = "Категория: Диплом".encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    cat, desc, raw = classify_with_llm("текст", ["Диплом", "Аттестат"], "fake-model", ".")
    assert cat == "Диплом"
    assert desc == ""
    assert "Категория" in raw

def test_classify_with_llm_case_insensitive_parsing(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = "КАТЕГОРИЯ: Диплом\nОПИСАНИЕ: Документ".encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    cat, desc, raw = classify_with_llm("текст", ["Диплом", "Аттестат"], "fake-model", ".")
    assert cat == "Диплом"
    assert desc == "Документ"
    assert "КАТЕГОРИЯ" in raw or "ОПИСАНИЕ" in raw

def test_classify_with_llm_multiline_output(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = "Категория: Диплом\nОписание: Документ о высшем образовании\nДополнительная информация".encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    cat, desc, raw = classify_with_llm("текст", ["Диплом", "Аттестат"], "fake-model", ".")
    assert cat == "Диплом"
    assert desc == "Документ о высшем образовании"
    assert "Дополнительная информация" in raw

def test_classify_with_llm_with_stderr(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = "Категория: Диплом\nОписание: Документ".encode('utf-8')
            stderr = "Warning: some warning".encode('utf-8')
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    cat, desc, raw = classify_with_llm("текст", ["Диплом", "Аттестат"], "fake-model", ".")
    assert cat == "Диплом"
    assert desc == "Документ"
    assert "Warning" not in raw  # raw is only stdout

def test_classify_with_llm_empty_output(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = b""
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    cat, desc, raw = classify_with_llm("текст", ["Диплом", "Аттестат"], "fake-model", ".")
    assert cat == "Иное"
    assert desc == ""
    assert raw == ""

def test_classify_with_llm_text_truncation(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = "Категория: Диплом\nОписание: Документ".encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    # Test with very long text that should be truncated
    long_text = "Очень длинный текст " * 200  # More than 2000 characters
    cat, desc, raw = classify_with_llm(long_text, ["Диплом", "Аттестат"], "fake-model", ".")
    assert cat == "Диплом"
    assert desc == "Документ"
    assert "Категория" in raw
