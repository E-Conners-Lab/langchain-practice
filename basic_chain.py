"""Basic chain example with LangCHain and Ollama."""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize the model
llm = OllamaLLM(model="llama3.2")

# Create prompt template
template = PromptTemplate(
    input_variables=["protocol"],
    template="List 3 common troubleshooting steps for {protocol} issues. Be concise."
)

# Create a chain using LCEL (Langchain Expression Language)
chain = template | llm | StrOutputParser()

# Run the chain
result = chain.invoke({"protocol": "BGP"})
print(result)
