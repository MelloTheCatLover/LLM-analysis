from typing import List, Dict

SECTION_PREFIXES = {
    "1.": "Документы об образовании",
    "2.": "Научные публикации",
    "3.": "Участие в конференциях",
    "4.": "Олимпиады и конкурсы",
    "5.": "НИР и гранты",
    "6.": "Педагогическая деятельность",
    "7.": "Общественная и спортивная деятельность",
}

def get_section(cat: str) -> str:
    for pfx, sec in SECTION_PREFIXES.items():
        if cat.startswith(pfx):
            return sec
    return "Прочее"

def analyze_portfolio(docs: List[Dict]) -> Dict:
    presence = {sec: [] for sec in SECTION_PREFIXES.values()}
    presence["Прочее"] = []
    comments, total, maximum = [], 0, 0

    for d in docs:
        sec = get_section(d["detected"])
        presence[sec].append(d)

    scores = {}
    for sec, items in presence.items():
        unique = len({doc["detected"] for doc in items})
        scores[sec] = {"score": unique, "max": unique or 1}
        total += scores[sec]["score"]
        maximum += scores[sec]["max"]

    for sec, info in scores.items():
        s, m = info["score"], info["max"]
        if s == 0:
            comments.append(f"[{sec}] — нет документов.")
        else:
            comments.append(f"[{sec}] — {s} из {m} представлены.")
        # можно здесь добавить детальные проверки per-document

    pct = (total / maximum * 100) if maximum else 0
    overall = ("Сильное" if pct>=80 else "Среднее" if pct>=50 else "Требует доработки")

    return {
        "scores": scores,
        "total_score": total,
        "max_score": maximum,
        "percent": round(pct,1),
        "overall_assessment": overall,
        "comments": comments
    }
