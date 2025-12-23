"""Agent that uses custom tools to solve problems."""

from langchain_ollama import OllamaLLM
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import ipaddress


# Define tools
@tool
def calculate_subnet(cidr: str) -> str:
    """Calculate subnet details from CIDR notation. Input should be like '192.168.1.0/24'."""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return f"Network: {network.network_address}, Broadcast: {network.broadcast_address}, Mask: {network.netmask}, Usable hosts: {network.num_addresses - 2}"
    except ValueError as e:
        return f"Error: {str(e)}"


@tool
def lookup_vlan(vlan_id: int) -> str:
    """Look up VLAN information by ID number."""
    vlan_db = {
        10: {"name": "USERS", "subnet": "192.168.10.0/24"},
        20: {"name": "SERVERS", "subnet": "192.168.20.0/24"},
        30: {"name": "MANAGEMENT", "subnet": "192.168.30.0/24"},
    }
    if vlan_id in vlan_db:
        vlan = vlan_db[vlan_id]
        return f"VLAN {vlan_id}: {vlan['name']}, Subnet: {vlan['subnet']}"
    return f"VLAN {vlan_id} not found"


@tool
def check_interface(interface: str) -> str:
    """Check interface status. Input should be interface name like 'GigabitEthernet0/1'."""
    interfaces = {
        "GigabitEthernet0/1": "up/up, VLAN 10, 1Gbps",
        "GigabitEthernet0/2": "down/down, VLAN 20, auto",
        "GigabitEthernet0/3": "up/up, VLAN 30, 100Mbps",
    }
    if interface in interfaces:
        return f"{interface}: {interfaces[interface]}"
    return f"Interface {interface} not found"


# Tool registry
tools = {
    "calculate_subnet": calculate_subnet,
    "lookup_vlan": lookup_vlan,
    "check_interface": check_interface,
}

# Initialize model
llm = OllamaLLM(model="llama3.2")

# Prompt that asks the model to decide which tool to use
router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a network engineering assistant with access to these tools:

1. calculate_subnet - Calculate subnet details from CIDR notation (e.g., "192.168.1.0/24")
2. lookup_vlan - Look up VLAN information by ID number (e.g., 10, 20, 30)
3. check_interface - Check interface status (e.g., "GigabitEthernet0/1")

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


def parse_tool_response(response: str) -> tuple[str, str]:
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

    # Step 3: Execute the tool
    if tool_name in tools:
        print(f"Executing tool: {tool_name}")
        print(f"With input: {tool_input}")

        # Convert input for the tool
        if tool_name == "lookup_vlan":
            tool_result = tools[tool_name].invoke({"vlan_id": int(tool_input)})
        elif tool_name == "calculate_subnet":
            tool_result = tools[tool_name].invoke({"cidr": tool_input})
        elif tool_name == "check_interface":
            tool_result = tools[tool_name].invoke({"interface": tool_input})
        else:
            tool_result = "Unknown tool"

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

# Test the agent
print("=" * 50)
print("TOOL-USING AGENT TEST")
print("=" * 50)

questions = [
    "What subnet is VLAN 10 on and how many hosts can it support?",
    "Is GigabitEthernet0/2 up? What VLAN is it on?",
    "Calculate the subnet details for 172.16.0.0/20",
]

for question in questions:
    result = run_agent(question)
    print(f"\nFinal Answer: {result}")
    print("\n" + "=" * 50)