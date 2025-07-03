import os
import json
import pytest
from src.main import main

def test_main_runs(tmp_path, monkeypatch):
    # Подменяем файлы и конфиги
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Создаём фиктивный файл
    test_file = input_dir / "doc.pdf"
    test_file.write_text("dummy content")

    # Подменяем конфиги
    monkeypatch.setattr("src.main.INPUT_DIR", str(input_dir))
    monkeypatch.setattr("src.main.OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr("src.main.MANIFEST", [{
        "filename": "doc.pdf",
        "claimed_type": "Диплом бакалавра",
        "expected_name": "Иванов Иван Иванович"
    }])
    monkeypatch.setattr("src.main.TESSERACT_CFG", {"lang": "eng", "model": "fake-model"})

    # Подменяем функции, чтобы не запускать тяжелые процессы
    monkeypatch.setattr("src.processors.ocr.extract_text", lambda *a, **k: "Текст документа")
    monkeypatch.setattr("src.processors.llm_client.classify_with_llm", lambda *a, **k: ("Диплом бакалавра", "Тест"))
    monkeypatch.setattr("src.processors.classifier.compute_similarity", lambda a,b: 1.0)
    monkeypatch.setattr("src.processors.classifier.is_match", lambda a,b: True)
    monkeypatch.setattr("src.processors.name_extractor.extract_person_name", lambda *a, **k: {"full_name":"Иванов Иван Иванович", "match_with_expected":True, "comment":"OK"})
    monkeypatch.setattr("src.processors.portfolio_analyzer.analyze_portfolio", lambda *a, **k: {"scores":{}, "total_score":1, "max_score":1, "percent":100, "overall_assessment":"Сильное", "comments":[]})

    main()

    assert (output_dir / "details.xlsx").exists()
    assert (output_dir / "summary.json").exists()

def test_main_with_multiple_files(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Создаём несколько фиктивных файлов
    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    for file in files:
        test_file = input_dir / file
        test_file.write_text("dummy content")

    # Подменяем конфиги
    monkeypatch.setattr("src.main.INPUT_DIR", str(input_dir))
    monkeypatch.setattr("src.main.OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr("src.main.MANIFEST", [
        {"filename": "doc1.pdf", "claimed_type": "Диплом бакалавра", "expected_name": "Иванов Иван"},
        {"filename": "doc2.pdf", "claimed_type": "Аттестат", "expected_name": "Петров Петр"},
        {"filename": "doc3.pdf", "claimed_type": "Сертификат", "expected_name": ""}
    ])
    monkeypatch.setattr("src.main.TESSERACT_CFG", {"lang": "eng", "model": "fake-model"})

    # Подменяем функции
    monkeypatch.setattr("src.processors.ocr.extract_text", lambda *a, **k: "Текст документа")
    monkeypatch.setattr("src.processors.llm_client.classify_with_llm", lambda *a, **k: ("Диплом бакалавра", "Тест"))
    monkeypatch.setattr("src.processors.classifier.compute_similarity", lambda a,b: 0.8)
    monkeypatch.setattr("src.processors.classifier.is_match", lambda a,b: True)
    monkeypatch.setattr("src.processors.name_extractor.extract_person_name", lambda *a, **k: {"full_name":"Иванов Иван", "match_with_expected":True, "comment":"OK"})
    monkeypatch.setattr("src.processors.portfolio_analyzer.analyze_portfolio", lambda *a, **k: {"scores":{}, "total_score":3, "max_score":3, "percent":100, "overall_assessment":"Сильное", "comments":[]})

    main()

    assert (output_dir / "details.xlsx").exists()
    assert (output_dir / "summary.json").exists()

def test_main_with_missing_file(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Создаём только один файл, но в манифесте указано два
    test_file = input_dir / "doc1.pdf"
    test_file.write_text("dummy content")

    monkeypatch.setattr("src.main.INPUT_DIR", str(input_dir))
    monkeypatch.setattr("src.main.OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr("src.main.MANIFEST", [
        {"filename": "doc1.pdf", "claimed_type": "Диплом бакалавра", "expected_name": "Иванов Иван"},
        {"filename": "missing.pdf", "claimed_type": "Аттестат", "expected_name": "Петров Петр"}
    ])
    monkeypatch.setattr("src.main.TESSERACT_CFG", {"lang": "eng", "model": "fake-model"})

    # Подменяем функции
    monkeypatch.setattr("src.processors.ocr.extract_text", lambda *a, **k: "Текст документа")
    monkeypatch.setattr("src.processors.llm_client.classify_with_llm", lambda *a, **k: ("Диплом бакалавра", "Тест"))
    monkeypatch.setattr("src.processors.classifier.compute_similarity", lambda a,b: 1.0)
    monkeypatch.setattr("src.processors.classifier.is_match", lambda a,b: True)
    monkeypatch.setattr("src.processors.name_extractor.extract_person_name", lambda *a, **k: {"full_name":"Иванов Иван", "match_with_expected":True, "comment":"OK"})
    monkeypatch.setattr("src.processors.portfolio_analyzer.analyze_portfolio", lambda *a, **k: {"scores":{}, "total_score":1, "max_score":1, "percent":100, "overall_assessment":"Сильное", "comments":[]})

    main()

    assert (output_dir / "details.xlsx").exists()
    assert (output_dir / "summary.json").exists()

def test_main_with_no_expected_name(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    test_file = input_dir / "doc.pdf"
    test_file.write_text("dummy content")

    monkeypatch.setattr("src.main.INPUT_DIR", str(input_dir))
    monkeypatch.setattr("src.main.OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr("src.main.MANIFEST", [{
        "filename": "doc.pdf",
        "claimed_type": "Диплом бакалавра",
        "expected_name": ""  # No expected name
    }])
    monkeypatch.setattr("src.main.TESSERACT_CFG", {"lang": "eng", "model": "fake-model"})

    # Подменяем функции
    monkeypatch.setattr("src.processors.ocr.extract_text", lambda *a, **k: "Текст документа")
    monkeypatch.setattr("src.processors.llm_client.classify_with_llm", lambda *a, **k: ("Диплом бакалавра", "Тест"))
    monkeypatch.setattr("src.processors.classifier.compute_similarity", lambda a,b: 1.0)
    monkeypatch.setattr("src.processors.classifier.is_match", lambda a,b: True)
    monkeypatch.setattr("src.processors.name_extractor.extract_person_name", lambda *a, **k: {})
    monkeypatch.setattr("src.processors.portfolio_analyzer.analyze_portfolio", lambda *a, **k: {"scores":{}, "total_score":1, "max_score":1, "percent":100, "overall_assessment":"Сильное", "comments":[]})

    main()

    assert (output_dir / "details.xlsx").exists()
    assert (output_dir / "summary.json").exists()

def test_main_with_different_similarity_scores(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    test_file = input_dir / "doc.pdf"
    test_file.write_text("dummy content")

    monkeypatch.setattr("src.main.INPUT_DIR", str(input_dir))
    monkeypatch.setattr("src.main.OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr("src.main.MANIFEST", [{
        "filename": "doc.pdf",
        "claimed_type": "Диплом бакалавра",
        "expected_name": "Иванов Иван Иванович"
    }])
    monkeypatch.setattr("src.main.TESSERACT_CFG", {"lang": "eng", "model": "fake-model"})

    # Подменяем функции с разными значениями сходства
    monkeypatch.setattr("src.processors.ocr.extract_text", lambda *a, **k: "Текст документа")
    monkeypatch.setattr("src.processors.llm_client.classify_with_llm", lambda *a, **k: ("Диплом магистра", "Тест"))
    monkeypatch.setattr("src.processors.classifier.compute_similarity", lambda a,b: 0.6)  # Different similarity
    monkeypatch.setattr("src.processors.classifier.is_match", lambda a,b: False)  # No match
    monkeypatch.setattr("src.processors.name_extractor.extract_person_name", lambda *a, **k: {"full_name":"Петров Петр", "match_with_expected":False, "comment":"Не совпадает"})
    monkeypatch.setattr("src.processors.portfolio_analyzer.analyze_portfolio", lambda *a, **k: {"scores":{}, "total_score":1, "max_score":1, "percent":100, "overall_assessment":"Сильное", "comments":[]})

    main()

    assert (output_dir / "details.xlsx").exists()
    assert (output_dir / "summary.json").exists()

def test_main_with_empty_manifest(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    monkeypatch.setattr("src.main.INPUT_DIR", str(input_dir))
    monkeypatch.setattr("src.main.OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr("src.main.MANIFEST", [])  # Empty manifest
    monkeypatch.setattr("src.main.TESSERACT_CFG", {"lang": "eng", "model": "fake-model"})

    # Подменяем функции
    monkeypatch.setattr("src.processors.portfolio_analyzer.analyze_portfolio", lambda *a, **k: {"scores":{}, "total_score":0, "max_score":0, "percent":0, "overall_assessment":"Слабое", "comments":[]})

    main()

    assert not (output_dir / "details.xlsx").exists()
    assert not (output_dir / "summary.json").exists()
