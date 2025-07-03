import json
from src.processors.name_extractor import extract_person_name

def test_extract_person_name_json(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = '{ "full_name": "Иванов Иван Иванович", "match_with_expected": true, "comment": "Тест" }'.encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = extract_person_name("текст", "Иванов Иван Иванович", "fake-model", ".")
    assert isinstance(res, dict)
    assert res.get("full_name") == "Иванов Иван Иванович"

def test_extract_person_name_no_match(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = '{ "full_name": "Петров Петр Петрович", "match_with_expected": false, "comment": "Не совпадает" }'.encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = extract_person_name("текст", "Иванов Иван Иванович", "fake-model", ".")
    assert isinstance(res, dict)
    assert res.get("full_name") == "Петров Петр Петрович"
    assert res.get("match_with_expected") is False

def test_extract_person_name_empty_expected(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = '{ "full_name": "Сидоров Сидор Сидорович", "match_with_expected": null, "comment": "Нет ожидаемого имени" }'.encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = extract_person_name("текст", "", "fake-model", ".")
    assert isinstance(res, dict)
    assert res.get("full_name") == "Сидоров Сидор Сидорович"
    assert "match_with_expected" not in res or res.get("match_with_expected") is None

def test_extract_person_name_invalid_json(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = 'invalid json'.encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = extract_person_name("текст", "Иванов Иван Иванович", "fake-model", ".")
    assert isinstance(res, dict)
    assert res == {"raw": "invalid json"}  # Invalid JSON returns raw output

def test_extract_person_name_missing_fields(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = '{ "full_name": "Иванов Иван" }'.encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = extract_person_name("текст", "Иванов Иван Иванович", "fake-model", ".")
    assert isinstance(res, dict)
    assert res.get("full_name") == "Иванов Иван"
    assert "match_with_expected" not in res
    assert "comment" not in res

def test_extract_person_name_with_stderr(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = '{ "full_name": "Иванов Иван Иванович", "match_with_expected": true, "comment": "Тест" }'.encode('utf-8')
            stderr = "Warning: some warning".encode('utf-8')
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = extract_person_name("текст", "Иванов Иван Иванович", "fake-model", ".")
    assert isinstance(res, dict)
    assert res.get("full_name") == "Иванов Иван Иванович"

def test_extract_person_name_empty_output(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = b""
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = extract_person_name("текст", "Иванов Иван Иванович", "fake-model", ".")
    assert isinstance(res, dict)
    assert res == {"raw": ""}  # Empty output returns raw empty string

def test_extract_person_name_different_name_formats(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = '{ "full_name": "Иванов-Петров Иван", "match_with_expected": true, "comment": "Двойная фамилия" }'.encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = extract_person_name("текст", "Иванов-Петров Иван", "fake-model", ".")
    assert isinstance(res, dict)
    assert res.get("full_name") == "Иванов-Петров Иван"

def test_extract_person_name_with_special_characters(monkeypatch):
    def fake_run(*args, **kwargs):
        class Result:
            stdout = '{ "full_name": "О\'Коннор Джон", "match_with_expected": false, "comment": "Специальные символы" }'.encode('utf-8')
            stderr = b""
        return Result()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = extract_person_name("текст", "О'Коннор Джон", "fake-model", ".")
    assert isinstance(res, dict)
    assert res.get("full_name") == "О'Коннор Джон"
