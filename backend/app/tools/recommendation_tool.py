from app.services.crop_recommendation import rank_crops


def crop_recommendation_tool(crop_analysis, preferred_crop=None, budget=None):
    """
    Rank candidate crops using deterministic scoring.

    Parameters
    ----------
    crop_analysis   : list from analyze_all_candidates()
    preferred_crop  : optional crop mentioned by farmer (noted, not forced)
    budget          : optional farmer budget in Rs
    """
    return rank_crops(
        crop_analysis,
        preferred_crop=preferred_crop,
        budget=budget,
    )
