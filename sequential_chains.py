"""Sequential chains where output of one becomes input of the next."""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize the model
llm = OllamaLLM(model="llama3.2")

# Chain 1:Identify the problem from symptoms
identify_prompt = PromptTemplate(
    input_variables=["symptoms"],
    template="""You are network engineer. Based on these symptoms, identify the most likely problem in one sentence.

Symptoms: {symptoms}    

Problem:"""
)

# Chain 2 Suggest troubleshooting steps for that problem
troubleshoot_prompt = PromptTemplate(
    input_variables=["problem"],
    template="""Given this network problem, list 3 specific troubleshooting commands to run on a Cisco device.
    
Problem: {problem}

Commands:"""
)

# Chain 3: Explain what to look for in the output
analyze_prompt = PromptTemplate(
    input_variables=["commands"],
    template="""For these troubleshooting commands, explain what to look for  in the output that would confirm the issue.

Commands: {commands}
    
What to look for:"""
)

# Build individual chains
chain1 = identify_prompt | llm | StrOutputParser()
chain2 = troubleshoot_prompt | llm | StrOutputParser()
chain3 = analyze_prompt | llm | StrOutputParser()

def troubleshoot_workflow(symptoms: str) -> dict:
    """Run the full troubleshooting workflow."""
    print("=" * 50)
    print("NETWORK TROUBLESHOOTING WORKFLOW")
    print("=" * 50)

    print(f"\nSYMPTOMS: {symptoms}\n")

    # Step 1: Identify problem
    problem = chain1.invoke({"symptoms": symptoms})
    print(f"IDENTIFIED PROBLEM:\n{problem}\n")

    # Step 2: Output of chain1 feeds into chain2
    commands = chain2.invoke({"problem": problem})
    print(f"TROUBLESHOOTING COMMANDS:\n{commands}\n")

    # Step 3: Output of chain2 feeds into chain3
    analysis = chain3.invoke({"commands": commands})
    print(f"WHAT TO LOOK FOR:\n{commands}\n")

    return {
        "problem": problem,
        "commands": commands,
        "analysis": analysis
    }


#Test it
result = troubleshoot_workflow(
    "Users in VLAN 10 can ping the gateway but cannot reach servers in VLAN 20."
    "Inter-VLAN routing was working yesterday."
)