"""Network Chatbot combining tools, RAG, and memory."""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from rag_setup import get_vector_store
import ipaddress

# ===== MODEL CONFIGURATION =====
# Using Qwen2.5 for better tool calling accuracy
# Other options: "llama3.1", "mistral", "llama3.3:70b"
MODEL_NAME = "qwen2.5"


# ===== TOOLS =====

@tool
def calculate_subnet(cidr: str) -> str:
    """Calculate subnet details from CIDR notation like '192.168.1.0/24'."""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return f"Network: {network.network_address}, Broadcast: {network.broadcast_address}, Mask: {network.netmask}, Usable hosts: {network.num_addresses - 2}"
    except ValueError as e:
        return f"Error: {str(e)}"


@tool
def lookup_vlan(vlan_id: int) -> str:
    """Look up VLAN information by ID number."""
    vlan_db = {
        10: {"name": "USERS", "subnet": "192.168.10.0/24", "gateway": "192.168.10.1"},
        20: {"name": "SERVERS", "subnet": "192.168.20.0/24", "gateway": "192.168.20.1"},
        30: {"name": "MANAGEMENT", "subnet": "192.168.30.0/24", "gateway": "192.168.30.1"},
    }
    if vlan_id in vlan_db:
        vlan = vlan_db[vlan_id]
        return f"VLAN {vlan_id}: {vlan['name']}, Subnet: {vlan['subnet']}, Gateway: {vlan['gateway']}"
    return f"VLAN {vlan_id} not found"


@tool
def check_interface(interface: str) -> str:
    """Check interface status like 'GigabitEthernet0/1'."""
    interfaces = {
        "GigabitEthernet0/1": "up/up, VLAN 10, 1Gbps, Full duplex",
        "GigabitEthernet0/2": "down/down, VLAN 20, auto, auto",
        "GigabitEthernet0/3": "up/up, VLAN 30, 100Mbps, Full duplex",
    }
    if interface in interfaces:
        return f"{interface}: {interfaces[interface]}"
    return f"Interface {interface} not found"


@tool
def get_ospf_neighbors(device: str) -> str:
    """Get OSPF neighbor information for a device like 'R1'."""
    ospf_data = {
        "R1": "Neighbor 192.168.1.2 (R2): FULL/DR on Gi0/0\nNeighbor 192.168.1.3 (R3): FULL/BDR on Gi0/0",
        "R2": "Neighbor 192.168.1.1 (R1): FULL/BDR on Gi0/0\nNeighbor 192.168.1.3 (R3): FULL/DR on Gi0/0",
    }
    if device in ospf_data:
        return f"OSPF neighbors for {device}:\n{ospf_data[device]}"
    return f"No OSPF data for {device}"


@tool
def get_bgp_summary(device: str) -> str:
    """Get BGP summary for a device like 'R1'."""
    bgp_data = {
        "R1": "Neighbor 10.0.0.2 (AS 65002): Established, 150 prefixes\nNeighbor 10.0.0.3 (AS 65003): Established, 200 prefixes\nNeighbor 10.0.0.4 (AS 65004): Idle, 0 prefixes",
        "R2": "Neighbor 10.0.0.1 (AS 65001): Established, 120 prefixes",
    }
    if device in bgp_data:
        return f"BGP summary for {device}:\n{bgp_data[device]}"
    return f"No BGP data for {device}"


@tool
def ping_device(target: str) -> str:
    """Ping a target IP address."""
    ping_results = {
        "192.168.10.1": "Success: 5/5 packets, avg latency 1ms",
        "192.168.20.1": "Success: 5/5 packets, avg latency 2ms",
        "192.168.30.1": "Failed: 0/5 packets, destination unreachable",
        "8.8.8.8": "Success: 5/5 packets, avg latency 15ms",
    }
    if target in ping_results:
        return f"Ping {target}: {ping_results[target]}"
    return f"Ping {target}: Host unreachable"


@tool
def get_interface_errors(interface: str) -> str:
    """Get error counters for an interface like 'GigabitEthernet0/1'."""
    error_data = {
        "GigabitEthernet0/1": "Input errors: 0, Output errors: 0, CRC: 0, Collisions: 0 - HEALTHY",
        "GigabitEthernet0/2": "Input errors: 1542, Output errors: 23, CRC: 847, Collisions: 156 - ERRORS DETECTED",
        "GigabitEthernet0/3": "Input errors: 5, Output errors: 0, CRC: 5, Collisions: 0 - MINOR ISSUES",
    }
    if interface in error_data:
        return f"{interface}: {error_data[interface]}"
    return f"Interface {interface} not found"


@tool
def get_routing_table(device: str) -> str:
    """Get routing table for a device like 'R1'."""
    routing_tables = {
        "R1": """0.0.0.0/0 via 10.0.0.1 (static)
192.168.10.0/24 directly connected, Gi0/1
192.168.20.0/24 via 192.168.1.2 (OSPF)
192.168.30.0/24 via 192.168.1.3 (OSPF)""",
        "R2": """0.0.0.0/0 via 10.0.0.1 (OSPF)
192.168.10.0/24 via 192.168.1.1 (OSPF)
192.168.20.0/24 directly connected, Gi0/1""",
    }
    if device in routing_tables:
        return f"Routing table for {device}:\n{routing_tables[device]}"
    return f"No routing data for {device}"


# Tool registry
TOOLS = {
    "calculate_subnet": calculate_subnet,
    "lookup_vlan": lookup_vlan,
    "check_interface": check_interface,
    "get_ospf_neighbors": get_ospf_neighbors,
    "get_bgp_summary": get_bgp_summary,
    "ping_device": ping_device,
    "get_interface_errors": get_interface_errors,
    "get_routing_table": get_routing_table,
}

TOOL_DESCRIPTIONS = """Available tools:
1. calculate_subnet - Calculate subnet details. Input: CIDR notation (e.g., "192.168.1.0/24")
2. lookup_vlan - Look up VLAN info. Input: VLAN ID number (e.g., 10)
3. check_interface - Check interface status. Input: interface name (e.g., "GigabitEthernet0/1")
4. get_ospf_neighbors - Get OSPF neighbors. Input: device name (e.g., "R1")
5. get_bgp_summary - Get BGP summary. Input: device name (e.g., "R1")
6. ping_device - Ping a target. Input: IP address (e.g., "192.168.10.1")
7. get_interface_errors - Get interface error counters. Input: interface name (e.g., "GigabitEthernet0/1")
8. get_routing_table - Get routing table. Input: device name (e.g., "R1")"""


# ===== RAG SETUP =====

def search_documentation(query: str, k: int = 2) -> str:
    """Search network documentation for relevant information."""
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search(query, k=k)
        if results:
            return "\n\n".join([doc.page_content for doc in results])
        return "No relevant documentation found."
    except Exception as e:
        return f"Documentation search error: {str(e)}"


# ===== CHATBOT =====

class NetworkChatbot:
    """Interactive network assistant with tools, RAG, and memory."""

    def __init__(self, model: str = MODEL_NAME):
        self.llm = OllamaLLM(model=model)
        self.model_name = model
        self.chat_history = []

        # Router prompt - decides what action to take
        self.router_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a network engineering assistant that routes questions to the right action.

{TOOL_DESCRIPTIONS}

Based on the user's question, respond with EXACTLY ONE of these formats:

If the question needs device/network data, respond:
ACTION: TOOL
TOOL_NAME: <tool_name>
TOOL_INPUT: <input_value>

If the question is about troubleshooting steps or procedures, respond:
ACTION: DOCS
QUERY: <search_terms>

If you can answer directly without tools or docs, respond:
ACTION: DIRECT
ANSWER: <your_answer>

Important:
- Pick only ONE action
- For TOOL_INPUT, provide only the value, no quotes
- For VLAN lookups, provide just the number
- Match tool names exactly as listed above"""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])

        # Response prompt - formulates final answer
        self.response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful network engineering assistant. 
Use the provided context to answer the question.
Be concise, technical, and actionable.
If the context doesn't fully answer the question, acknowledge that."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", """Question: {question}

Context:
{context}

Answer:""")
        ])

    def _parse_router_response(self, response: str) -> dict:
        """Parse the router's decision."""
        lines = response.strip().split("\n")
        result = {"action": None}

        for line in lines:
            line = line.strip()
            if line.startswith("ACTION:"):
                result["action"] = line.replace("ACTION:", "").strip().upper()
            elif line.startswith("TOOL_NAME:"):
                result["tool_name"] = line.replace("TOOL_NAME:", "").strip().lower()
            elif line.startswith("TOOL_INPUT:"):
                result["tool_input"] = line.replace("TOOL_INPUT:", "").strip().strip('"').strip("'")
            elif line.startswith("QUERY:"):
                result["query"] = line.replace("QUERY:", "").strip()
            elif line.startswith("ANSWER:"):
                result["answer"] = line.replace("ANSWER:", "").strip()

        return result

    def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        """Execute a tool and return the result."""
        if tool_name not in TOOLS:
            return f"Unknown tool: {tool_name}"

        try:
            # Handle type conversion for specific tools
            if tool_name == "lookup_vlan":
                tool_input = {"vlan_id": int(tool_input)}
            elif tool_name == "calculate_subnet":
                tool_input = {"cidr": tool_input}
            elif tool_name in ["check_interface", "get_interface_errors"]:
                tool_input = {"interface": tool_input}
            elif tool_name in ["get_ospf_neighbors", "get_bgp_summary", "get_routing_table"]:
                tool_input = {"device": tool_input}
            elif tool_name == "ping_device":
                tool_input = {"target": tool_input}

            return TOOLS[tool_name].invoke(tool_input)
        except Exception as e:
            return f"Tool error: {str(e)}"

    def chat(self, question: str, verbose: bool = True) -> str:
        """Process a question and return a response."""

        # Step 1: Route the question
        router_chain = self.router_prompt | self.llm | StrOutputParser()
        router_response = router_chain.invoke({
            "history": self.chat_history,
            "question": question
        })

        parsed = self._parse_router_response(router_response)
        action = parsed.get("action", "DIRECT")

        # Step 2: Get context based on action
        context = ""

        if action == "TOOL":
            tool_name = parsed.get("tool_name", "")
            tool_input = parsed.get("tool_input", "")
            if verbose:
                print(f"  [Tool: {tool_name}({tool_input})]")
            context = self._execute_tool(tool_name, tool_input)

        elif action == "DOCS":
            query = parsed.get("query", question)
            if verbose:
                print(f"  [Docs: {query}]")
            context = search_documentation(query)

        elif action == "DIRECT":
            if parsed.get("answer"):
                self.chat_history.append(HumanMessage(content=question))
                self.chat_history.append(AIMessage(content=parsed["answer"]))
                return parsed["answer"]
            context = "Answer based on your networking knowledge."

        # Step 3: Generate final response
        response_chain = self.response_prompt | self.llm | StrOutputParser()
        response = response_chain.invoke({
            "history": self.chat_history,
            "question": question,
            "context": context
        })

        # Update history
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=response))

        return response

    def clear_history(self):
        """Clear conversation history."""
        self.chat_history = []
        print("History cleared.")


def main():
    """Run the interactive chatbot."""
    print("=" * 60)
    print("NETWORK ENGINEERING ASSISTANT")
    print(f"Model: {MODEL_NAME}")
    print("=" * 60)
    print("\nCapabilities:")
    print("  • Device status (OSPF, BGP, interfaces, routing)")
    print("  • Network calculations (subnets, VLANs)")
    print("  • Troubleshooting guidance (from documentation)")
    print("  • Conversation memory (remembers context)")
    print("\nCommands: 'quit' to exit, 'clear' to reset history")
    print("=" * 60)

    chatbot = NetworkChatbot()

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            print("Goodbye!")
            break

        if user_input.lower() == 'clear':
            chatbot.clear_history()
            continue

        response = chatbot.chat(user_input)
        print(f"\nAssistant: {response}")


if __name__ == "__main__":
    main()