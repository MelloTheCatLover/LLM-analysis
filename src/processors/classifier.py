import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def normalize_text(s: str) -> str:
    return " ".join(s.lower().split())

def compute_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    vec = TfidfVectorizer().fit_transform([a, b])
    return float(cosine_similarity(vec[0], vec[1])[0][0])

def is_match(detected: str, claimed: str, tfidf_threshold: float = 0.65, seq_threshold: float = 0.7) -> bool:
    sim = compute_similarity(detected, claimed)
    if sim >= tfidf_threshold:
        return True
    seq = difflib.SequenceMatcher(None, normalize_text(detected), normalize_text(claimed)).ratio()
    return seq >= seq_threshold
