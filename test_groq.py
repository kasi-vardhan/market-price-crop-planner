import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv("backend/.env")
load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=200,
)

response = llm.invoke("Reply with exactly: API connection successful")
print(response.content)
