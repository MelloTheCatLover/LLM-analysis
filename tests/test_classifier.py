from src.processors.classifier import compute_similarity, is_match

def test_compute_similarity_identical():
    a = "Документ об образовании"
    b = "Документ об образовании"
    sim = compute_similarity(a, b)
    assert sim > 0.9

def test_compute_similarity_similar():
    a = "Диплом бакалавра"
    b = "Диплом бакалавра по информатике"
    sim = compute_similarity(a, b)
    assert 0.5 < sim < 1.0

def test_compute_similarity_different():
    a = "Диплом"
    b = "Аттестат"
    sim = compute_similarity(a, b)
    assert sim < 0.5

def test_compute_similarity_empty_strings():
    sim = compute_similarity("", "")
    assert sim == 0.0  # Empty strings return 0.0, not 1.0

def test_compute_similarity_one_empty():
    sim1 = compute_similarity("Диплом", "")
    sim2 = compute_similarity("", "Диплом")
    assert sim1 == sim2
    assert sim1 < 0.3

def test_compute_similarity_case_insensitive():
    a = "ДИПЛОМ"
    b = "диплом"
    sim = compute_similarity(a, b)
    assert sim > 0.8

def test_is_match_true_and_false():
    assert is_match("Диплом", "Диплом") is True
    assert is_match("Диплом", "Аттестат", tfidf_threshold=0.5) is False

def test_is_match_with_different_thresholds():
    # Test with high threshold
    assert is_match("Диплом", "Диплом бакалавра", tfidf_threshold=0.9) is False
    # Test with low threshold
    assert is_match("Диплом", "Диплом бакалавра", tfidf_threshold=0.1) is True

def test_is_match_case_insensitive():
    assert is_match("ДИПЛОМ", "диплом") is True
    assert is_match("Диплом", "ДИПЛОМ") is True

def test_is_match_with_whitespace():
    assert is_match(" Диплом ", "Диплом") is True
    assert is_match("Диплом", "  Диплом  ") is True

def test_is_match_empty_strings():
    assert is_match("", "") is True
    assert is_match("Диплом", "") is False
    assert is_match("", "Диплом") is False
