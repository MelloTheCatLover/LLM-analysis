from src.processors.portfolio_analyzer import analyze_portfolio

def test_analyze_portfolio_basic():
    docs = [
        {"detected": "1. Диплом бакалавра"},
        {"detected": "2. Список научных публикаций"},
        {"detected": "2. Список научных публикаций"},
        {"detected": "7. Грамота / благодарность"}
    ]
    result = analyze_portfolio(docs)
    assert "scores" in result
    assert result["total_score"] > 0

def test_analyze_portfolio_empty_list():
    docs = []
    result = analyze_portfolio(docs)
    assert "scores" in result
    assert result["total_score"] == 0
    assert result["max_score"] == 8  # Max score is sum of all section maxes (7 sections + "Прочее")
    assert result["percent"] == 0
    assert result["overall_assessment"] == "Требует доработки"  # Less than 50% is "Требует доработки"

def test_analyze_portfolio_single_document():
    docs = [{"detected": "1. Диплом бакалавра"}]
    result = analyze_portfolio(docs)
    assert "scores" in result
    assert result["total_score"] > 0
    assert result["max_score"] > 0
    assert result["percent"] > 0

def test_analyze_portfolio_all_categories():
    docs = [
        {"detected": "1. Диплом бакалавра"},
        {"detected": "2. Список научных публикаций"},
        {"detected": "3. Сертификаты о прохождении курсов"},
        {"detected": "4. Дипломы олимпиад и конкурсов"},
        {"detected": "5. Рекомендательные письма"},
        {"detected": "6. Мотивационное письмо"},
        {"detected": "7. Грамота / благодарность"},
        {"detected": "8. Иное"}
    ]
    result = analyze_portfolio(docs)
    assert "scores" in result
    assert result["total_score"] > 0
    assert result["max_score"] > 0
    assert result["percent"] > 0

def test_analyze_portfolio_duplicate_documents():
    docs = [
        {"detected": "1. Диплом бакалавра"},
        {"detected": "1. Диплом бакалавра"},  # Duplicate
        {"detected": "2. Список научных публикаций"},
        {"detected": "2. Список научных публикаций"}  # Duplicate
    ]
    result = analyze_portfolio(docs)
    assert "scores" in result
    assert result["total_score"] > 0

def test_analyze_portfolio_unknown_categories():
    docs = [
        {"detected": "Неизвестная категория"},
        {"detected": "Другая неизвестная категория"},
        {"detected": "1. Диплом бакалавра"}
    ]
    result = analyze_portfolio(docs)
    assert "scores" in result
    assert result["total_score"] > 0

def test_analyze_portfolio_mixed_case():
    docs = [
        {"detected": "1. ДИПЛОМ БАКАЛАВРА"},
        {"detected": "2. список научных публикаций"},
        {"detected": "3. Сертификаты о прохождении курсов"}
    ]
    result = analyze_portfolio(docs)
    assert "scores" in result
    assert result["total_score"] > 0

def test_analyze_portfolio_with_whitespace():
    docs = [
        {"detected": " 1. Диплом бакалавра "},
        {"detected": "2. Список научных публикаций  "},
        {"detected": "  3. Сертификаты о прохождении курсов"}
    ]
    result = analyze_portfolio(docs)
    assert "scores" in result
    assert result["total_score"] > 0

def test_analyze_portfolio_high_score_scenario():
    docs = [
        {"detected": "1. Диплом бакалавра"},
        {"detected": "1. Диплом магистра"},
        {"detected": "2. Список научных публикаций"},
        {"detected": "3. Сертификаты о прохождении курсов"},
        {"detected": "4. Дипломы олимпиад и конкурсов"},
        {"detected": "5. Рекомендательные письма"},
        {"detected": "6. Мотивационное письмо"},
        {"detected": "7. Грамота / благодарность"}
    ]
    result = analyze_portfolio(docs)
    assert "scores" in result
    assert result["total_score"] > 0
    assert result["percent"] > 50  # Should be a high percentage

def test_analyze_portfolio_low_score_scenario():
    docs = [
        {"detected": "8. Иное"},
        {"detected": "Неизвестная категория"},
        {"detected": "Другая неизвестная категория"}
    ]
    result = analyze_portfolio(docs)
    assert "scores" in result
    assert result["total_score"] >= 0
    assert result["percent"] <= 30  # Should be a low percentage
