from app.agents.agriculture_graph import agriculture_graph


result = agriculture_graph.invoke({

    "farmer_question": """
    I have 2 acres of red soil near Markapur.
    I have medium water availability.
    Which crop should I consider?
    """,

    "location": "markapur",

    "soil": "red",

    "water": "medium",

    "season": "kharif",

    "land_area": 2,

    "messages": []
})


print("\n====================================")
print("AGENTIC AGRICULTURE RESULT")
print("====================================")


for message in result["messages"]:

    print("\n------------------------------------")

    if hasattr(message, "content") and message.content:

        print(message.content)

    if hasattr(message, "tool_calls"):

        if message.tool_calls:

            print("\nTOOL CALLS:")

            for call in message.tool_calls:

                print(
                    "Tool:",
                    call["name"]
                )

                print(
                    "Arguments:",
                    call["args"]
                )
