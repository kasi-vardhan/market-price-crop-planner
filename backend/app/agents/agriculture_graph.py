from typing import Annotated, TypedDict, Any
import json

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from langchain_groq import ChatGroq
from langchain_core.tools import tool

from app.tools.weather_tool import weather_tool
from app.tools.market_tool import market_price_tool
from app.tools.crop_tool import crop_suitability_tool
from app.tools.profit_tool import profit_calculator_tool
from app.tools.rag_tool import rag_search_tool
from app.tools.recommendation_tool import crop_recommendation_tool
from app.services.candidate_analysis import analyze_all_candidates
from app.services.climate import get_historical_rainfall
from app.services.source_citation import build_source_citations


# ============================================================
# STATE
# ============================================================

class AgricultureState(TypedDict, total=False):

    farmer_question: str

    location: str
    soil: str
    water: str
    season: str
    land_area: float
    budget: float | None  # optional farmer investment budget in Rs

    messages: Annotated[list[Any], add_messages]

    tool_results: list[dict]

    climate_data: dict

    weather_data: dict

    candidate_analysis: list[dict]

    ranking_result: dict

    source_citations: list[dict]


from app.services.llm_factory import get_llm

llm = get_llm()


# ============================================================
# TOOLS
# ============================================================

@tool
def get_weather(location: str):
    """
    Get current weather information.
    """
    return weather_tool(location)


@tool
def get_market_information(crop: str):
    """
    Get market information for a crop.
    """
    return market_price_tool(crop)


@tool
def check_crop_suitability(
    crop: str,
    soil: str,
    water: str,
    season: str,
    temperature: float | None = None,
    rainfall: float | None = None
):
    """
    Calculate crop suitability.
    """
    return crop_suitability_tool(
        crop=crop,
        soil=soil,
        water=water,
        season=season,
        temperature=temperature if temperature is not None else 25.0,
        rainfall=rainfall if rainfall is not None else 1000.0
    )


@tool
def calculate_profit(
    crop: str,
    yield_per_acre: float | None = None,
    expected_price: float | None = None,
    cost_per_acre: float | None = None,
    land_area: float | None = None
):
    """
    Deterministically calculate crop revenue,
    cost and profit.
    """
    return profit_calculator_tool(
        crop=crop,
        yield_per_acre=yield_per_acre or 0.0,
        expected_price=expected_price or 0.0,
        cost_per_acre=cost_per_acre or 0.0,
        land_area=land_area or 1.0
    )


@tool
def search_agricultural_knowledge(
    query: str,
    crop: str | None = None
):
    """
    Search agricultural knowledge.

    Use crop when the question is specifically
    about a known crop.
    """
    from app.tools.rag_tool import rag_search_tool

    return rag_search_tool(
        query=query,
        crop=crop,
        top_k=3
    )


TOOLS = [
    get_weather,
    get_market_information,
    check_crop_suitability,
    calculate_profit,
    search_agricultural_knowledge
]


llm_with_tools = llm.bind_tools(TOOLS)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an agricultural evidence-gathering agent.

Your job is to collect the information required
for crop planning.

Available tools:

1. Weather
2. Market information
3. Crop suitability
4. Profit calculation
5. Agricultural knowledge retrieval

IMPORTANT:

- Use tools instead of guessing.
- Never invent market prices.
- Never invent weather information.
- Never calculate financial values manually.
- Never guarantee profit.
- Use market status exactly as returned.
- Cached data must never be described as live.
- Use agricultural knowledge retrieval when useful.

RAG SEARCH RULES:

1. Use the agricultural knowledge tool when
   agricultural knowledge is needed.

2. If the question concerns a specific crop,
   provide that crop to the knowledge search tool.

3. Prefer crop-specific documents over general
   agricultural documents.

4. Do not treat retrieved agricultural information
   as universal when the source is region-specific.

5. Do not invent information that is not present
   in the retrieved evidence.

6. Preserve source information from the retrieval
   results.

You are responsible for gathering evidence.

You are NOT responsible for choosing the final crop.

A separate deterministic Python ranking engine
will choose the final recommendation.

Therefore:

DO NOT produce a final crop recommendation
during the evidence-gathering stage.

Gather the necessary evidence and stop.
"""


# ============================================================
# AGENT NODE
# ============================================================

def agent_node(state: AgricultureState):
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

    existing_messages = state.get(
        "messages",
        []
    )

    budget = state.get("budget")
    budget_str = f"Rs {budget:,.0f}" if budget else "Not specified"

    farm_context = f"""
Farmer question:
{state["farmer_question"]}

Farm details:
Location: {state["location"]}
Soil: {state["soil"]}
Water availability: {state["water"]}
Season: {state["season"]}
Land area: {state["land_area"]} acres
Investment budget: {budget_str}

Collect the evidence required to compare the available crops.
"""
    system_msg = SystemMessage(content=SYSTEM_PROMPT)
    user_msg = HumanMessage(content=farm_context)

    # Limit tool gathering to at most 2 rounds to ensure fast, deterministic response
    ai_turns = sum(1 for m in existing_messages if type(m).__name__ == "AIMessage")
    if ai_turns >= 2:
        return {
            "messages": [AIMessage(content="Proceeding to candidate analysis and deterministic crop ranking with gathered context.")]
        }

    if not existing_messages:
        messages = [system_msg, user_msg]
    else:
        messages = [system_msg, user_msg] + list(existing_messages)

    try:
        response = llm_with_tools.invoke(messages)
    except Exception as exc:
        # If Groq hits rate limit or error, safely proceed with empty tool call
        response = AIMessage(content="Proceeding to candidate analysis and deterministic crop ranking with gathered context.")

    return {
        "messages": [response]
    }


# ============================================================
# COLLECT TOOL RESULTS
# ============================================================

def collect_tool_results(
    state: AgricultureState
):

    results = []

    for message in state.get(
        "messages",
        []
    ):

        if type(message).__name__ != "ToolMessage":
            continue

        tool_name = getattr(
            message,
            "name",
            "unknown"
        )

        content = getattr(
            message,
            "content",
            None
        )

        parsed_content = content

        if isinstance(content, str):

            try:
                parsed_content = json.loads(
                    content
                )

            except (
                json.JSONDecodeError,
                TypeError
            ):
                parsed_content = content

        results.append(
            {
                "tool": tool_name,
                "result": parsed_content
            }
        )

    return {
        "tool_results": results
    }


# ============================================================
# CANDIDATE ANALYSIS NODE
# ============================================================

def candidate_analysis_node(
    state: AgricultureState
):
    """
    Analyze every configured crop using deterministic
    Python logic.
    """

    weather = None

    for item in state.get(
        "tool_results",
        []
    ):

        if item.get("tool") == "get_weather":

            weather = item.get("result")

            break

    if not isinstance(weather, dict) or "error" in weather or weather.get("temperature") is None:
        weather = weather_tool(state["location"])

    if not isinstance(weather, dict) or "error" in weather:
        weather = {
            "location": state["location"],
            "temperature": 25.0,
            "daily_rainfall": 0.0,
            "rainfall": 1000.0,
            "status": "fallback",
            "source": "climatology"
        }

    temperature = weather.get(
        "temperature"
    )

    if temperature is None:
        temperature = 25

    climate = get_historical_rainfall(
        location=state["location"],
        season=state["season"],
        years=3
    )

    rainfall_source = "historical"

    if (
        climate.get("status")
        == "available"
    ):

        rainfall = climate.get(
            "average_seasonal_rainfall_mm"
        )

    else:

        rainfall = 1000
        rainfall_source = "fallback"

    analysis = analyze_all_candidates(
        soil=state["soil"],
        water=state["water"],
        season=state["season"],
        temperature=temperature,
        rainfall=rainfall,
        land_area=state["land_area"],
        state="Andhra Pradesh",
        budget=state.get("budget"),
    )

    climate_data = {
        **climate,
        "rainfall_used_mm": rainfall,
        "rainfall_source": rainfall_source
    }

    return {
        "candidate_analysis": analysis,
        "climate_data": climate_data,
        "weather_data": weather
    }


# ============================================================
# DETERMINISTIC RANKING NODE
# ============================================================

# ============================================================
# DETERMINISTIC RANKING NODE
# ============================================================

def ranking_node(
    state: AgricultureState
):

    crop_analysis = state.get(
        "candidate_analysis",
        []
    )

    if not crop_analysis:

        return {
            "ranking_result": {
                "error": (
                    "Candidate crop analysis "
                    "could not be generated."
                )
            }
        }

    from app.rag.crop_detection import detect_crop
    farmer_q = state.get("farmer_question", "")
    detected_crop = detect_crop(farmer_q)

    ranking_result = crop_recommendation_tool(
        crop_analysis,
        preferred_crop=detected_crop,
        budget=state.get("budget"),
    )

    return {
        "ranking_result": ranking_result
    }


# ============================================================
# CITATION NODE
# ============================================================

def citation_node(
    state: AgricultureState
):

    knowledge_results = []

    for item in state.get(
        "tool_results",
        []
    ):

        if item.get("tool") == (
            "search_agricultural_knowledge"
        ):

            result = item.get(
                "result"
            )

            if isinstance(
                result,
                list
            ):

                knowledge_results.extend(
                    result
                )

    rec_crop = None
    if state.get("ranking_result"):
        rec_crop = state["ranking_result"].get("recommended_crop")

    # Guarantee verified agronomic evidence for the recommended crop
    if rec_crop:
        try:
            from app.tools.rag_tool import rag_search_tool
            retrieved = rag_search_tool(
                query=f"{rec_crop} crop cultivation requirements season soil water",
                crop=rec_crop,
                top_k=2
            )
            if isinstance(retrieved, list) and retrieved:
                knowledge_results = retrieved + [k for k in knowledge_results if k.get("crop") != rec_crop]
        except Exception:
            pass

    # Filter knowledge results so that if a crop is recommended (e.g. tomato),
    # we don't display citations for unrecommended crops (e.g. groundnut)
    if rec_crop:
        filtered = [
            k for k in knowledge_results
            if str(k.get("crop", "")).lower() in (rec_crop.lower(), "general", "")
        ]
        if filtered:
            knowledge_results = filtered

    citations = build_source_citations(
        knowledge_results
    )

    return {
        "source_citations": citations
    }


# ============================================================
# FINAL LLM NODE
# ============================================================

FINAL_PROMPT = """
You are the final agricultural decision-support assistant.

You have been given:
1. The farmer's actual farm inputs (location, soil, water availability, season, land area).
2. Evidence collected by tools (weather, market prices).
3. The deterministic crop ranking calculated by the Python ranking engine.

Your job is ONLY to explain the calculated ranking to the farmer.

CRITICAL RULES:
1. STRICT FARMER INPUT FIDELITY:
   - The farmer's soil type is explicitly provided. You MUST state the farmer's exact soil type (e.g., if the farmer has red soil, say their soil is red soil).
   - NEVER claim the farmer has a different soil type (e.g. NEVER say 'loamy soil' when the farmer has 'red soil', even if a retrieved research paper or advisory mentions loamy soil in another location).
2. DETERMINISTIC RECOMMENDATION:
   - The recommended crop comes strictly from the deterministic ranking engine.
   - Do NOT change the recommended crop or choose another crop independently.
   - Clearly state the recommended crop and its recommendation score.
   - Explain why this crop achieved the top score: detail how the farmer's actual soil, water availability, season, and local weather influenced the ranking.
3. OTHER EVALUATED CROPS:
   - Mention the other crops evaluated by the ranking engine and their exact scores.
   - Briefly explain why they ranked lower (e.g. water mismatches, soil suitability differences, or lower margins).
4. FINANCIAL AND MARKET SITUATION:
   - State the market price, mandi location, and calculated profit directly from the provided financial data.
   - Explain that market data is cached and actual prices at mandi arrival may vary.
   - Never guarantee profit.

Structure your response clearly:
- Recommended Crop
- Why This Crop (Explain influence of actual soil, water availability, season, and weather)
- Other Evaluated Crops (List runner-ups and their scores)
- Market & Profit Analysis (Actual mandi price, consistent units, expected financial result)
- Risk and Uncertainty Advisories
Keep the answer simple, practical, and useful for a farmer.
"""


def final_answer_node(
    state: AgricultureState
):

    ranking = state.get(
        "ranking_result",
        {}
    )

    source_citations = state.get(
        "source_citations",
        []
    )

    farmer_soil = state.get("soil", "red")
    farmer_water = state.get("water", "high")
    farmer_season = state.get("season", "kharif")
    farmer_land = state.get("land_area", 1.0)
    farmer_loc = state.get("location", "Markapur")

    rec_crop = ranking.get("recommended_crop", "Tomato")
    rec_score = ranking.get("recommendation_score", 0)
    ranked_crops_list = ranking.get("ranked_crops", [])

    compact_sources = [
        {
            "title": s.get("title"),
            "organization": s.get("organization"),
            "url": s.get("url"),
            "passage": (s.get("passage") or "")[:200]
        }
        for s in source_citations[:3]
    ]

    other_crops_summary = [
        f"{c.get('crop', '').capitalize()} (Score: {c.get('recommendation_score', 0)}%, Suitability: {c.get('suitability', {}).get('score', 0)}%)"
        for c in ranked_crops_list
        if str(c.get("crop", "")).lower() != str(rec_crop).lower()
    ]

    top_crop_item = ranked_crops_list[0] if ranked_crops_list else {}
    top_profit_data = top_crop_item.get("profit", {})
    expected_price = top_profit_data.get("expected_price", 25)
    net_profit = top_profit_data.get("profit")

    user_prompt = f"""
FARMER'S ACTUAL FARM CONDITIONS:
- Location: {farmer_loc}
- Soil: {farmer_soil} soil
- Water availability: {farmer_water}
- Season: {farmer_season}
- Land area: {farmer_land} acres

DETERMINISTIC RANKING ENGINE OUTPUT:
- #1 Recommended Crop: {str(rec_crop).capitalize()} (Recommendation Score: {rec_score}%)
- Other Evaluated Crops: {', '.join(other_crops_summary) if other_crops_summary else 'None'}

FINANCIAL ANALYSIS:
- Mandi Price: ₹{expected_price} / kg (₹{expected_price * 100 if isinstance(expected_price, (int, float)) else 'N/A'} / quintal)
- Total Estimated Profit: ₹{net_profit} (for {farmer_land} acres)

RETRIEVED AGRONOMIC ADVISORIES:
{json.dumps(compact_sources, ensure_ascii=False)}

MANDATORY INSTRUCTIONS:
- Specifically mention that the farmer's soil is {farmer_soil} soil.
- Do NOT refer to loamy soil or any other soil as the farmer's soil.
- Explain why {str(rec_crop).capitalize()} was selected based on {farmer_soil} soil, {farmer_water} water, and {farmer_season} season.
- Mention the other evaluated crops ({', '.join(other_crops_summary)}) and their scores.
"""

    messages = [
        {
            "role": "system",
            "content": FINAL_PROMPT
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    try:
        response = llm.invoke(messages)
    except Exception as exc:
        top_crop = str(rec_crop).capitalize()
        fallback_text = (
            f"Based on agricultural decision parameters for {farmer_loc} ({farmer_season} season, {farmer_soil} soil), "
            f"the recommended crop for your farm is **{top_crop}**.\n\n"
            f"- Recommended Crop: {top_crop} (Score: {rec_score}%)\n"
            f"- Land Area: {farmer_land} acres\n"
            f"- Water Requirement: {farmer_water.capitalize()}\n"
            f"- Other Evaluated Crops: {', '.join(other_crops_summary)}\n\n"
            f"Please review the detailed weather forecast, market status, and financial breakdown below."
        )
        from langchain_core.messages import AIMessage
        response = AIMessage(content=fallback_text)

    return {
        "messages": [response]
    }


# ============================================================
# AGENT ROUTING
# ============================================================

def should_continue(
    state: AgricultureState
):

    last_message = state["messages"][-1]

    tool_calls = getattr(
        last_message,
        "tool_calls",
        None
    )

    if tool_calls:

        return "tools"

    return "collect_results"


# ============================================================
# GRAPH
# ============================================================

def build_agriculture_graph():

    graph = StateGraph(
        AgricultureState
    )

    graph.add_node(
        "agent",
        agent_node
    )

    graph.add_node(
        "tools",
        ToolNode(TOOLS)
    )

    graph.add_node(
        "collect_results",
        collect_tool_results
    )

    graph.add_node(
        "candidate_analysis",
        candidate_analysis_node
    )

    graph.add_node(
        "ranking",
        ranking_node
    )

    graph.add_node(
        "citations",
        citation_node
    )

    graph.add_node(
        "final_answer",
        final_answer_node
    )

    graph.add_edge(
        START,
        "agent"
    )

    graph.add_conditional_edges(
        "agent",
        should_continue
    )

    graph.add_edge(
        "tools",
        "agent"
    )

    graph.add_edge(
        "collect_results",
        "candidate_analysis"
    )

    graph.add_edge(
        "candidate_analysis",
        "ranking"
    )

    graph.add_edge(
        "ranking",
        "citations"
    )

    graph.add_edge(
        "citations",
        "final_answer"
    )

    graph.add_edge(
        "final_answer",
        END
    )

    return graph.compile()


agriculture_graph = build_agriculture_graph()

