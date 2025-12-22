"""Practicing prompt templates with LangChain and Ollama."""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Initialize model
llm = OllamaLLM(model="llama3.2")

# Create a prompt template
template = PromptTemplate(
    input_variables=["topic", "audience"],
    template="Explain {topic} to a {audience}. Keep it under 100 words."
)

# Format the prompt
prompt = template.format(topic="OSPF routing protocol", audience="beginner network engineer")

# Get response
response = llm.invoke(prompt)
print(response)



