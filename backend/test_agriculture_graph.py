from app.agents.agriculture_graph import agriculture_graph


result = agriculture_graph.invoke(
    {
        "farmer_question": (
            "What crop should I grow this season "
            "for better profitability?"
        ),

        "location": "Markapur",

        "soil": "red",

        "water": "high",

        "season": "kharif",

        "land_area": 2
    }
)


print("\n==============================")
print("AGRICULTURE AGENT RESULT")
print("==============================\n")


messages = result.get("messages", [])

for message in messages:

    print(
        "\nMESSAGE TYPE:",
        type(message).__name__
    )

    if hasattr(message, "content"):

        if message.content:
            print(
                "\nCONTENT:\n",
                message.content
            )

    if hasattr(message, "tool_calls"):

        if message.tool_calls:
            print(
                "\nTOOL CALLS:\n",
                message.tool_calls
            )
