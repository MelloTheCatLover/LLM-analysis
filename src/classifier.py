import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    try:
        vec = TfidfVectorizer().fit_transform([a, b])
        sim = float(cosine_similarity(vec[0], vec[1])[0][0])
    except Exception:
        sim = 0.0
    return sim

def is_match(detected: str, claimed: str, tfidf_threshold: float = 0.65, seq_threshold: float = 0.7) -> bool:
    sim = compute_similarity(detected, claimed)
    if sim >= tfidf_threshold:
        return True
    seq = difflib.SequenceMatcher(None, detected.lower(), claimed.lower()).ratio()
    return seq >= seq_threshold
