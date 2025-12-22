"""Chat prompt templates with LangChain and Ollama"""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Initialize the model
llm = OllamaLLM(model="llama3.2")

# Create chat prompt template
chat_template = ChatPromptTemplate.from_messages([
    ("system", "You are a senior network engineer. Answer questions concisely and technically."),
    ("human", "{question}")
])

# Create chain
chain = chat_template | llm

# Ask questions
questions = [
    "What causes OSPF to be stuck in EXSTART state?",
    "When would you use eBGP multihop?",
    "What is the difference between access and trunk ports?"
]

for question in questions:
    print(f"Q: {question}")
    response = chain.invoke({"question": question})
    print(f"A: {response}\n")
    print("-" * 50 + "\n")