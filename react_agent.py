"""Agent that uses custom tools to solve problems."""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import tools from custom_tools.py instead of redefining them
from custom_tools import (
    calculate_subnet,
    lookup_vlan,
    check_port_status,
    ping_check,
    get_routing_table,
    get_ospf_neighbors,
    get_bgp_summary,
    get_interface_errors,
    generate_acl,
)

# Tool registry with metadata for dynamic invocation
tools = {
    "calculate_subnet": {
        "func": calculate_subnet,
        "param": "cidr",
        "type": str,
        "desc": "Calculate subnet details from CIDR notation (e.g., '192.168.1.0/24')"
    },
    "lookup_vlan": {
        "func": lookup_vlan,
        "param": "vlan_id",
        "type": int,
        "desc": "Look up VLAN info by ID (e.g., 10, 20, 30, 99, 100)"
    },
    "check_port_status": {
        "func": check_port_status,
        "param": "interface",
        "type": str,
        "desc": "Check interface status (e.g., 'GigabitEthernet0/1')"
    },
    "ping_check": {
        "func": ping_check,
        "param": "target",
        "type": str,
        "desc": "Ping an IP address (e.g., '192.168.10.1', '8.8.8.8')"
    },
    "get_routing_table": {
        "func": get_routing_table,
        "param": "device",
        "type": str,
        "desc": "Get routing table for a device (e.g., 'R1', 'R2', 'SW1')"
    },
    "get_ospf_neighbors": {
        "func": get_ospf_neighbors,
        "param": "device",
        "type": str,
        "desc": "Get OSPF neighbors for a device (e.g., 'R1', 'R2', 'R3')"
    },
    "get_bgp_summary": {
        "func": get_bgp_summary,
        "param": "device",
        "type": str,
        "desc": "Get BGP summary for a device (e.g., 'R1', 'R2')"
    },
    "get_interface_errors": {
        "func": get_interface_errors,
        "param": "interface",
        "type": str,
        "desc": "Get error counters for interface (e.g., 'GigabitEthernet0/2')"
    },
    "generate_acl": {
        "func": generate_acl,
        "param": "params",
        "type": str,
        "desc": "Generate ACL config. Format: 'permit|deny,source,dest,protocol,port'"
    },
}

# Build tool descriptions dynamically for the prompt
tool_descriptions = "\n".join(
    f"{i+1}. {name} - {info['desc']}"
    for i, (name, info) in enumerate(tools.items())
)

# Initialize model
llm = OllamaLLM(model="llama3.2")

# Prompt that asks the model to decide which tool to use
router_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are a network engineering assistant with access to these tools:

{tool_descriptions}

Given a question, decide which tool to use and what input to provide.
Respond in exactly this format:
TOOL: <tool_name>
INPUT: <input_value>

If no tool is needed, respond:
TOOL: none
ANSWER: <your direct answer>"""),
    ("human", "{question}")
])

router_chain = router_prompt | llm | StrOutputParser()


def parse_tool_response(response: str) -> tuple[str, str, str]:
    """Parse the model's tool selection response."""
    lines = response.strip().split("\n")
    tool_name = None
    tool_input = None
    answer = None

    for line in lines:
        if line.startswith("TOOL:"):
            tool_name = line.replace("TOOL:", "").strip().lower()
        elif line.startswith("INPUT:"):
            tool_input = line.replace("INPUT:", "").strip()
        elif line.startswith("ANSWER:"):
            answer = line.replace("ANSWER:", "").strip()

    return tool_name, tool_input, answer


def run_agent(question: str) -> str:
    """Run the agent on a question."""
    print(f"\nQuestion: {question}")
    print("-" * 40)

    # Step 1: Ask the model which tool to use
    response = router_chain.invoke({"question": question})
    print(f"Model's decision:\n{response}\n")

    # Step 2: Parse the response
    tool_name, tool_input, direct_answer = parse_tool_response(response)

    # Clean up tool_input - remove quotes if present
    if tool_input:
        tool_input = tool_input.strip('"').strip("'")

    if tool_name == "none" or tool_name is None:
        print(f"No tool needed. Direct answer: {direct_answer}")
        return direct_answer or response

    # Step 3: Execute the tool dynamically
    if tool_name in tools:
        tool_info = tools[tool_name]
        print(f"Executing tool: {tool_name}")
        print(f"With input: {tool_input}")

        # Convert input to correct type and invoke
        try:
            typed_input = tool_info["type"](tool_input)
            tool_result = tool_info["func"].invoke({tool_info["param"]: typed_input})
        except (ValueError, TypeError) as e:
            tool_result = f"Error invoking tool: {e}"

        print(f"\nTool result: {tool_result}")

        # Step 4: Let the model formulate a final answer
        final_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a helpful network engineering assistant. Use the tool result to answer the question concisely."),
            ("human", f"Question: {question}\n\nTool result: {tool_result}\n\nProvide a helpful answer:")
        ])
        final_chain = final_prompt | llm | StrOutputParser()
        final_answer = final_chain.invoke({})

        return final_answer
    else:
        return f"Unknown tool: {tool_name}"


# Test the agent with various tools
if __name__ == "__main__":
    print("=" * 50)
    print("TOOL-USING AGENT TEST")
    print("=" * 50)

    questions = [
        # Original questions
        "What subnet is VLAN 10 on?",
        "Is GigabitEthernet0/2 up?",
        "Calculate the subnet details for 172.16.0.0/20",
        # New questions for new tools
        "Can you ping 192.168.10.1?",
        "Show me the routing table for R1",
        "What are the OSPF neighbors on R2?",
        "Is there a BGP peering issue on R1?",
        "Are there any errors on GigabitEthernet0/2?",
    ]

    for question in questions:
        result = run_agent(question)
        print(f"\nFinal Answer: {result}")
        print("\n" + "=" * 50)
