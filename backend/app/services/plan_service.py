"""
Plan Service — thin orchestration layer between the API route and the LangGraph agent.
"""

from app.agents.agriculture_graph import agriculture_graph


def generate_crop_plan(
    farmer_question: str | None,
    location: str,
    soil: str,
    water: str,
    season: str,
    land_area: float,
    budget: float | None = None,
) -> dict:
    """
    Invoke the LangGraph agriculture workflow and return a structured result.

    Parameters
    ----------
    farmer_question : optional natural-language question from the farmer
    location        : location string (mandal/district)
    soil, water, season : agronomic conditions
    land_area       : acres
    budget          : optional investment budget in Rs
    """
    effective_question = farmer_question or (
        f"Which crop should I plant on my {land_area}-acre {soil} soil farm "
        f"in {location} this {season} season?"
    )

    result = agriculture_graph.invoke(
        {
            "farmer_question": effective_question,
            "location": location,
            "soil": soil,
            "water": water,
            "season": season,
            "land_area": land_area,
            "budget": budget,
            "messages": [],
        }
    )

    messages = result.get("messages", [])
    tool_results = result.get("tool_results", [])
    ranking_result = result.get("ranking_result", {})

    final_message = None
    for message in reversed(messages):
        if type(message).__name__ != "AIMessage":
            continue
        content = getattr(message, "content", None)
        if content:
            final_message = content
            break

    return {
        "question": effective_question,
        "location": location,
        "recommendation": final_message,
        "tool_results": tool_results,
        "ranking": ranking_result,
        "climate_data": result.get("climate_data"),
        "weather_data": result.get("weather_data"),
        "source_citations": result.get("source_citations", []),
    }
