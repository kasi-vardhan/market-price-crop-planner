from app.agents.agriculture_agent import run_agriculture_agent
from app.services.llm_service import generate_agriculture_response


farmer_question = """
I have 2 acres of red soil near Markapur.
I have medium water availability.
Which crop should I consider?
"""


print("Running agriculture agent...")

agent_result = run_agriculture_agent(

    farmer_question=farmer_question,

    location="markapur",

    soil="red",

    water="medium",

    season="kharif",

    land_area=2
)


if "error" in agent_result:

    print("Agent Error:")
    print(agent_result["error"])

else:

    print("Generating AI explanation...")

    answer = generate_agriculture_response(
        farmer_question=farmer_question,
        agent_result=agent_result
    )

    print("\n")
    print("====================================")
    print("AI AGRICULTURE RECOMMENDATION")
    print("====================================")

    print(answer)
