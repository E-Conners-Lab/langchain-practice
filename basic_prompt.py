"""Basic LangChain example with Ollama."""

from langchain_ollama import OllamaLLM

# Initialize the model
llm = OllamaLLM(model="llama3.2")

# Simple invocation
response = llm.invoke("Explain what BGP is in two sentences.")
print(response)



