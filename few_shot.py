"""Few-shot prompting with LangChain and Ollama."""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate


# Initialize the model
llm = OllamaLLM(model="llama3.2")

# Define examples
examples = [
    {
        "command": "show ip route",
        "description": "Displays the routing table including all learned routes and their sources."
    },
    {
        "command": "sho ip ospf neighbor",
        "description": "Shows OSPF neighbor adjencies and their current state"
    },
    {
        "command": "show ip bgp summary",
        "description": "Displays BGP neighbor status and prefix counts"
    }
]

# Template for each example
example_template = PromptTemplate(
  input_variables=["command", "description"],
  template="Command: {command}\nDescription: {description}"
)

# Few-shot prompt template
few_shot_template = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_template,
    prefix="You are a network engineering assistant. Given a Cisco command, provide a brief description of what it does.\n\nExamples:",
    suffix="\nCommand: {input}\nDescription:",
    input_variables=["input"]
)

# Create chain
chain = few_shot_template | llm

# Test with a new command
result= chain.invoke({"input": "show cdp neighbors"})
print(result)

