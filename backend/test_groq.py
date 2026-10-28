from app.services.llm_factory import get_llm

llm = get_llm()
response = llm.invoke(
    "Reply with exactly: GROQ CONNECTION SUCCESS"
)

print(response.content)
