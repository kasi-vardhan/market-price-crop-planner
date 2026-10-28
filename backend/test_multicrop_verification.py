from app.services.candidate_analysis import analyze_all_candidates
from app.services.crop_recommendation import rank_crops
from app.rag.crop_detection import detect_crop

scenarios = [
    {"soil": "red", "water": "high", "season": "kharif", "q": "What crop should I grow with good water?"},
    {"soil": "clay", "water": "high", "season": "kharif", "q": "I have heavy clay soil with canal water."},
    {"soil": "black", "water": "medium", "season": "kharif", "q": "What grows well on black soil with medium water?"},
    {"soil": "sandy", "water": "medium", "season": "kharif", "q": "Which crop is suited to sandy soil?"},
    {"soil": "red", "water": "medium", "season": "kharif", "q": "Can I grow groundnut on my red soil farm?"},
    {"soil": "red", "water": "medium", "season": "kharif", "q": "Is chilli a good option for me?"}
]

for s in scenarios:
    preferred = detect_crop(s["q"])
    cand = analyze_all_candidates(soil=s["soil"], water=s["water"], season=s["season"], temperature=28.0, rainfall=900.0, land_area=2.0)
    res = rank_crops(cand, preferred_crop=preferred)
    rec = res["recommended_crop"]
    score = res["recommendation_score"]
    print(f"Soil: {s['soil']:5s} | Question: {s['q'][:40]:40s} | Target: {str(preferred):9s} => Recommended: {rec.upper()} ({score:.1f}%)")
