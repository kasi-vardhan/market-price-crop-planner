"""
Crop Ranking Engine — Transparent, budget-aware, suitability-first ranking.

Scoring dimensions and weights (initial, tunable):
  Agronomic suitability   30%
  Affordability           20%
  Expected profitability  25%
  Return on Investment    10%
  Market outlook          10%
  Risk / confidence        5%

Essential eligibility rules (applied before scoring):
  - "ineligible" crops (soil or season violation) cannot rank above eligible crops.
  - Crops that exceed the farmer's stated budget are excluded from eligible ranking.
  - Negative-profit crops are shown but clearly flagged.

Scoring normalization:
  All component scores are on a 0–100 scale before weighting.
  Affordability: 100 if total_cost ≤ budget, degrades proportionally above budget.
  ROI: Normalized against the highest positive ROI in the candidate set.
  Profitability: Normalized against the highest positive profit in the candidate set.
"""

import statistics


# ---------------------------------------------------------------------------
# SCORING WEIGHTS — configurable
# ---------------------------------------------------------------------------
RANKING_WEIGHTS = {
    "suitability": 0.30,
    "affordability": 0.20,
    "profitability": 0.25,
    "roi": 0.10,
    "market_outlook": 0.10,
    "risk": 0.05,
}


# ---------------------------------------------------------------------------
# COMPONENT SCORERS
# ---------------------------------------------------------------------------

def calculate_price_stability(prices: list) -> float:
    """Stability score from historical price coefficient of variation. 0–100."""
    if not prices or len(prices) < 2:
        return 50.0  # Neutral when insufficient data

    mean_price = statistics.mean(prices)
    if mean_price == 0:
        return 0.0

    std_dev = statistics.pstdev(prices)
    cv = std_dev / mean_price
    score = 100.0 / (1.0 + cv * 5.0)
    return round(max(0.0, min(100.0, score)), 2)


def calculate_market_outlook_score(outlook: str | None) -> float:
    """Market outlook string → 0–100 score."""
    if not outlook:
        return 50.0  # Neutral when unknown

    mapping = {
        "positive": 100.0,
        "stable": 60.0,
        "negative": 20.0,
        "unknown": 50.0,
    }
    return mapping.get(str(outlook).lower().strip(), 50.0)


def calculate_affordability_score(total_cost: float | None, budget: float | None) -> float:
    """
    Affordability score: 100 when total_cost ≤ budget.
    Degrades to 0 when total_cost ≥ 2× budget.
    Returns 100 when budget is not specified (no constraint).
    """
    if budget is None or budget <= 0:
        return 100.0  # No budget constraint provided

    if total_cost is None:
        return 50.0  # Neutral when cost data is missing

    if total_cost <= budget:
        return 100.0

    ratio = total_cost / budget  # > 1.0 means over budget
    score = 100.0 - (ratio - 1.0) * 100.0  # 1.0→100, 2.0→0
    return round(max(0.0, min(100.0, score)), 2)


def calculate_profit_score(profit: float | None, max_positive_profit: float) -> float:
    """Normalized profit score relative to best candidate. 0 for negative or missing."""
    if not isinstance(profit, (int, float)):
        return 0.0
    if profit <= 0:
        return 0.0
    if max_positive_profit <= 0:
        return 0.0
    return round(max(0.0, min(100.0, (profit / max_positive_profit) * 100.0)), 2)


def calculate_roi_score(roi_percent: float | None, max_positive_roi: float) -> float:
    """Normalized ROI score relative to best candidate. 0 for negative or missing."""
    if not isinstance(roi_percent, (int, float)):
        return 0.0
    if roi_percent <= 0:
        return 0.0
    if max_positive_roi <= 0:
        return 0.0
    return round(max(0.0, min(100.0, (roi_percent / max_positive_roi) * 100.0)), 2)


def calculate_risk_score(
    suitability_score: float,
    stability_score: float,
    market_outlook_score: float,
) -> float:
    """Composite risk/confidence score."""
    score = (
        suitability_score * 0.50
        + stability_score * 0.30
        + market_outlook_score * 0.20
    )
    return round(max(0.0, min(100.0, score)), 2)


def calculate_overall_score(
    suitability_score: float,
    affordability_score: float,
    profitability_score: float,
    roi_score: float,
    market_outlook_score: float,
    risk_score: float,
) -> float:
    """Weighted combination of all scoring dimensions."""
    score = (
        suitability_score * RANKING_WEIGHTS["suitability"]
        + affordability_score * RANKING_WEIGHTS["affordability"]
        + profitability_score * RANKING_WEIGHTS["profitability"]
        + roi_score * RANKING_WEIGHTS["roi"]
        + market_outlook_score * RANKING_WEIGHTS["market_outlook"]
        + risk_score * RANKING_WEIGHTS["risk"]
    )
    return round(max(0.0, min(100.0, score)), 2)


# ---------------------------------------------------------------------------
# DATA EXTRACTION HELPERS
# ---------------------------------------------------------------------------

def _get_profit_value(item: dict) -> float | None:
    profit_data = item.get("profit")
    if not isinstance(profit_data, dict):
        return None
    value = profit_data.get("profit")
    if isinstance(value, (int, float)):
        return value
    return None


def _get_roi_value(item: dict) -> float | None:
    profit_data = item.get("profit")
    if not isinstance(profit_data, dict):
        return None
    value = profit_data.get("roi_percent")
    if isinstance(value, (int, float)):
        return value
    return None


def _get_total_cost(item: dict) -> float | None:
    profit_data = item.get("profit")
    if not isinstance(profit_data, dict):
        return None
    value = profit_data.get("total_cost")
    if isinstance(value, (int, float)):
        return value
    return None


def _get_market_data(item: dict) -> tuple[dict, dict]:
    market_data = item.get("market")
    if not isinstance(market_data, dict):
        return {}, {}
    return market_data.get("current", {}), market_data.get("historical", {})


def _get_30_day_data(historical: dict) -> dict:
    data = historical.get("30_day")
    if not isinstance(data, dict):
        return {}
    return data


# ---------------------------------------------------------------------------
# REASON GENERATION
# ---------------------------------------------------------------------------

def generate_ranking_reasons(
    crop: str,
    eligibility_status: str,
    suitability_score: float,
    affordability_score: float,
    profitability_score: float,
    roi_score: float,
    market_outlook_score: float,
    stability_score: float,
    budget_exceeded: bool,
    essential_violations: list,
) -> list[str]:
    reasons = []

    if essential_violations:
        reasons.extend(essential_violations)
        return reasons  # Return only violation reasons for ineligible crops

    if budget_exceeded:
        reasons.append("Estimated cultivation cost exceeds the stated budget")

    if suitability_score >= 80:
        reasons.append("Strong agronomic suitability")
    elif suitability_score >= 60:
        reasons.append("Moderate agronomic suitability")
    else:
        reasons.append("Below-average agronomic suitability")

    if affordability_score >= 90:
        reasons.append("Well within budget")
    elif affordability_score >= 60:
        reasons.append("Moderate affordability")
    elif affordability_score < 60:
        reasons.append("Investment is above comfortable budget range")

    if profitability_score >= 80:
        reasons.append("Strong expected profitability")
    elif profitability_score >= 50:
        reasons.append("Reasonable expected profitability")
    elif profitability_score > 0:
        reasons.append("Below-average profitability among evaluated crops")
    else:
        reasons.append("No profit data available or profit is negative")

    if roi_score >= 80:
        reasons.append("High return on investment")
    elif roi_score >= 40:
        reasons.append("Moderate return on investment")

    if market_outlook_score >= 80:
        reasons.append("Positive recent market outlook")
    elif market_outlook_score >= 60:
        reasons.append("Stable recent market outlook")
    elif market_outlook_score < 40:
        reasons.append("Unfavorable recent market outlook")

    if stability_score >= 70:
        reasons.append("Relatively stable market prices")
    elif stability_score < 40:
        reasons.append("High price volatility — price risk is elevated")

    return reasons


# ---------------------------------------------------------------------------
# MAIN RANKING FUNCTION
# ---------------------------------------------------------------------------

def rank_crops(
    crop_analysis: list,
    preferred_crop: str | None = None,
    budget: float | None = None,
) -> dict:
    """
    Rank evaluated crops by a transparent, budget-aware multi-criterion score.

    Rules:
    1. Ineligible crops (soil or season violation) cannot outrank eligible crops.
    2. Crops exceeding the farmer's budget are flagged and penalized.
    3. Profit, ROI, and affordability scores are normalized against the best candidate.
    4. Incomplete data never receives a perfect score.

    Parameters
    ----------
    crop_analysis   : list of candidate dicts from analyze_all_candidates()
    preferred_crop  : optional; noted in output but does not override ranking
    budget          : optional farmer budget in Rs; triggers budget filtering

    Returns
    -------
    dict with recommended_crop, recommendation_score, ranked_crops
    """
    if not crop_analysis:
        return {
            "recommended_crop": None,
            "recommendation_score": 0.0,
            "ranked_crops": [],
            "no_eligible_crops_reason": "No crops were available for evaluation."
        }

    # ------------------------------------------------------------------
    # Pass 1: collect max positive profit and ROI for normalization
    # ------------------------------------------------------------------
    positive_profits = []
    positive_rois = []

    for item in crop_analysis:
        p = _get_profit_value(item)
        r = _get_roi_value(item)
        if isinstance(p, (int, float)) and p > 0:
            positive_profits.append(p)
        if isinstance(r, (int, float)) and r > 0:
            positive_rois.append(r)

    max_positive_profit = max(positive_profits) if positive_profits else 0.0
    max_positive_roi = max(positive_rois) if positive_rois else 0.0

    # ------------------------------------------------------------------
    # Pass 2: score each crop
    # ------------------------------------------------------------------
    ranked = []

    for item in crop_analysis:
        crop = item.get("crop")
        suitability = item.get("suitability") or {}
        comp_scores = suitability.get("component_scores") or {}

        soil_score = comp_scores.get("soil", 0.0)
        season_score = comp_scores.get("season", 0.0)
        water_score = comp_scores.get("water", 0.0)
        suitability_score = suitability.get("score", 0.0)
        eligibility_status = suitability.get("eligibility_status", "unknown")
        essential_violations = suitability.get("essential_constraint_violations", [])

        is_eligible = eligibility_status == "eligible"
        is_marginal = eligibility_status == "marginal"
        is_ineligible = eligibility_status == "ineligible"

        current_market, historical = _get_market_data(item)
        historical_30 = _get_30_day_data(historical)

        # Market components
        outlook = historical_30.get("outlook")
        market_outlook_score = calculate_market_outlook_score(outlook)
        prices = historical_30.get("prices", [])
        stability_score = calculate_price_stability(prices)

        # Financial components
        profit_value = _get_profit_value(item)
        roi_value = _get_roi_value(item)
        total_cost = _get_total_cost(item)

        # Budget assessment
        budget_exceeded = False
        if budget is not None and budget > 0 and total_cost is not None:
            budget_exceeded = total_cost > budget

        # Affordability score
        affordability_score = calculate_affordability_score(total_cost, budget)

        # For ineligible crops: effective profit = 0 (can't realise it)
        if is_ineligible:
            effective_profit = 0.0
            effective_roi = None
        else:
            effective_profit = profit_value
            effective_roi = roi_value

        profitability_score = calculate_profit_score(effective_profit, max_positive_profit)
        roi_score = calculate_roi_score(effective_roi, max_positive_roi)

        risk_score = calculate_risk_score(suitability_score, stability_score, market_outlook_score)

        overall_score = calculate_overall_score(
            suitability_score=suitability_score,
            affordability_score=affordability_score,
            profitability_score=profitability_score,
            roi_score=roi_score,
            market_outlook_score=market_outlook_score,
            risk_score=risk_score,
        )

        # Apply penalties for incompatibilities (on top of scoring)
        if is_ineligible:
            # Ineligible crops are heavily penalized but still visible
            overall_score = round(overall_score * 0.40, 2)
        elif is_marginal:
            overall_score = round(overall_score * 0.75, 2)

        if budget_exceeded and not is_ineligible:
            # Budget-busting crops get a moderate penalty
            overall_score = round(overall_score * 0.85, 2)

        market_status = current_market.get("status", "unknown")
        history_quality = historical_30.get("data_quality", "insufficient")

        reasons = generate_ranking_reasons(
            crop=crop,
            eligibility_status=eligibility_status,
            suitability_score=suitability_score,
            affordability_score=affordability_score,
            profitability_score=profitability_score,
            roi_score=roi_score,
            market_outlook_score=market_outlook_score,
            stability_score=stability_score,
            budget_exceeded=budget_exceeded,
            essential_violations=essential_violations,
        )

        ranked.append({
            "crop": crop,
            "recommendation_score": overall_score,
            "overall_score": overall_score,
            "eligibility_status": eligibility_status,
            "is_eligible": is_eligible or is_marginal,
            "is_marginal": is_marginal,
            "budget_exceeded": budget_exceeded,
            "component_scores": {
                "suitability": suitability_score,
                "affordability": affordability_score,
                "profitability": profitability_score,
                "roi": roi_score,
                "market_outlook": market_outlook_score,
                "price_stability": stability_score,
                "risk_confidence": risk_score,
            },
            "profit": item.get("profit"),
            "market": item.get("market"),
            "suitability": suitability,
            "data_quality": {
                "market_status": market_status,
                "historical_quality": history_quality,
            },
            "reasons": reasons,
        })

    # ------------------------------------------------------------------
    # Sort: strict priority groups + multi-level deterministic tie-breaking
    # Priority groups:
    #   0 = eligible + within budget (fully suitable and affordable)
    #   1 = marginal + within budget (minor water deficit, but affordable)
    #   2 = eligible + over budget   (suitable, but capital constrained)
    #   3 = marginal + over budget   (water deficit and over budget)
    #   4 = ineligible               (soil or season constraint violated)
    # ------------------------------------------------------------------
    def sort_key(item):
        status = item.get("eligibility_status", "unknown")
        over_budget = item.get("budget_exceeded", False)

        if status == "eligible" and not over_budget:
            group = 0
        elif status == "marginal" and not over_budget:
            group = 1
        elif status == "eligible" and over_budget:
            group = 2
        elif status == "marginal" and over_budget:
            group = 3
        else:
            group = 4

        suit_score = item.get("component_scores", {}).get("suitability", 0.0)
        return (group, -item["recommendation_score"], -suit_score, item.get("crop", ""))

    ranked.sort(key=sort_key)

    # Mark preferred crop if present
    if preferred_crop:
        target = str(preferred_crop).lower().strip()
        for item in ranked:
            if str(item.get("crop", "")).lower() == target:
                item["preferred_crop_match"] = True
                break

    for index, item in enumerate(ranked, start=1):
        item["rank"] = index

    best = ranked[0]

    # Determine if any crop is truly eligible
    eligible_count = sum(1 for c in ranked if c.get("eligibility_status") in ("eligible", "marginal") and not c.get("budget_exceeded"))

    result = {
        "recommended_crop": best["crop"],
        "recommendation_score": best["recommendation_score"],
        "ranked_crops": ranked,
        "eligible_crop_count": eligible_count,
        "budget": budget,
        "scoring_weights": RANKING_WEIGHTS,
    }

    if eligible_count == 0:
        if budget is not None:
            result["no_eligible_crops_reason"] = (
                "No crops satisfy both agronomic requirements (soil, season) "
                "and the stated budget. Consider increasing your budget, "
                "choosing a different season, or irrigating for water-intensive crops."
            )
        else:
            result["no_eligible_crops_reason"] = (
                "No crops satisfy the agronomic requirements for this soil type and season. "
                "The top-ranked crop above is shown as a best-available option only."
            )

    return result
