import json
from app.services.llm_factory import get_llm


def generate_agriculture_response(
    farmer_question,
    agent_result
):
    """
    Convert the structured agriculture-agent result
    into a farmer-friendly response.
    """

    agent_data = json.dumps(
        agent_result,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are an agricultural decision-support assistant.

Your job is to explain the results produced by an
agriculture planning system.

IMPORTANT RULES:

1. Use ONLY the information provided in the
   agent results.

2. Do NOT invent market prices.

3. Do NOT invent weather information.

4. Do NOT change or recalculate revenue,
   cost or profit.

5. Do NOT guarantee earnings.

6. Do NOT claim that a crop is definitely
   profitable.

7. Clearly mention uncertainty.

8. If information is missing, say that it
   is unavailable.

9. Keep the explanation simple and useful
   for a farmer.

10. Mention the knowledge sources when
    agricultural knowledge was retrieved.

FARMER QUESTION:

{farmer_question}

AGRICULTURE AGENT RESULTS:

{agent_data}

Prepare the answer using this structure:

Recommended Crop
Why This Crop
Weather Conditions
Market Situation
Estimated Financial Result
Main Risks
Important Caution
Sources
"""

    llm = get_llm()
    response = llm.invoke(prompt)

    return response.content


def generate_crop_explanation(
    crop_data: dict,
    farmer_question: str
) -> str:
    """
    Explain specific crop suitability and market financial results to a farmer.
    """
    crop_info = json.dumps(
        crop_data,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are an agricultural decision-support assistant.

Your task is to provide a clear, helpful explanation for a farmer regarding a specific crop.

FARMER QUESTION:
{farmer_question}

CROP DATA:
{crop_info}

Explain the suitability, expected market price, estimated revenue/costs/profit, and any key considerations in simple language.
"""

    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content

