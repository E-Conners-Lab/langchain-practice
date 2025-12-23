"""
Network Chatbot - LIVE VERSION
Connects to real lab devices using Scrapli

This version replaces simulated data with actual device queries.
Uses the same connection logic as your MCP server.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool

from scrapli.driver.core import AsyncIOSXEDriver
from scrapli.driver.generic import AsyncGenericDriver

# Load environment variables
load_dotenv()

# ===== CONFIGURATION =====
MODEL_NAME = "qwen2.5"

# Device credentials from environment
USERNAME = os.getenv("DEVICE_USERNAME", "admin")
PASSWORD = os.getenv("DEVICE_PASSWORD", "admin")

# Device inventory (matching your hosts.yml)
DEVICES = {
    "R1": {"host": "10.255.255.11", "device_type": "cisco_xe"},
    "R2": {"host": "10.255.255.12", "device_type": "cisco_xe"},
    "R3": {"host": "10.255.255.13", "device_type": "cisco_xe"},
    "R4": {"host": "10.255.255.14", "device_type": "cisco_xe"},
    "Switch-R1": {"host": "10.255.255.21", "device_type": "cisco_xe"},
    "Switch-R2": {"host": "10.255.255.22", "device_type": "cisco_xe"},
    "Switch-R4": {"host": "10.255.255.24", "device_type": "cisco_xe"},
    "Alpine-1": {"host": "10.255.255.110", "device_type": "linux"},
}


def get_scrapli_config(device_name: str) -> dict:
    """Get Scrapli connection config for a device."""
    if device_name not in DEVICES:
        return None

    device = DEVICES[device_name]
    return {
        "host": device["host"],
        "auth_username": USERNAME,
        "auth_password": PASSWORD,
        "auth_strict_key": False,
        "transport": "asyncssh",
        "timeout_socket": 10,
        "timeout_transport": 10,
    }


# ===== LIVE DEVICE FUNCTIONS =====

async def send_command_to_device(device_name: str, command: str) -> str:
    """Send a command to a real device and return output."""
    if device_name not in DEVICES:
        return f"Error: Device '{device_name}' not found. Available: {', '.join(DEVICES.keys())}"

    device = DEVICES[device_name]
    config = get_scrapli_config(device_name)

    try:
        if device["device_type"] == "linux":
            async with AsyncGenericDriver(**config) as conn:
                response = await conn.send_command(command)
                return response.result
        else:
            async with AsyncIOSXEDriver(**config) as conn:
                response = await conn.send_command(command)
                return response.result
    except Exception as e:
        return f"Error connecting to {device_name}: {str(e)}"


async def check_device_health(device_name: str) -> str:
    """Check health of a device."""
    if device_name not in DEVICES:
        return f"Error: Device '{device_name}' not found"

    device = DEVICES[device_name]
    config = get_scrapli_config(device_name)

    try:
        if device["device_type"] == "linux":
            async with AsyncGenericDriver(**config) as conn:
                response = await conn.send_command("uptime")
                return f"{device_name} is HEALTHY\nUptime: {response.result.strip()}"
        else:
            async with AsyncIOSXEDriver(**config) as conn:
                uptime = await conn.send_command("show version | include uptime")
                intf = await conn.send_command("show ip interface brief")

                # Count interfaces
                up_count = sum(
                    1 for line in intf.result.splitlines() if "up" in line.lower() and "admin" not in line.lower())
                down_count = sum(
                    1 for line in intf.result.splitlines() if "down" in line.lower() and "admin" not in line.lower())

                status = "HEALTHY" if down_count == 0 else "DEGRADED" if up_count > down_count else "CRITICAL"
                return f"{device_name} is {status}\n{uptime.result.strip()}\nInterfaces: {up_count} up, {down_count} down"
    except Exception as e:
        return f"{device_name} is CRITICAL - Error: {str(e)}"


async def get_ospf_neighbors_live(device_name: str) -> str:
    """Get OSPF neighbors from a real device."""
    output = await send_command_to_device(device_name, "show ip ospf neighbor")
    return f"OSPF Neighbors for {device_name}:\n{output}"


async def get_bgp_summary_live(device_name: str) -> str:
    """Get BGP summary from a real device."""
    output = await send_command_to_device(device_name, "show ip bgp summary")
    return f"BGP Summary for {device_name}:\n{output}"


async def get_interface_status_live(device_name: str, interface: str = None) -> str:
    """Get interface status from a real device."""
    if interface:
        output = await send_command_to_device(device_name, f"show interface {interface}")
    else:
        output = await send_command_to_device(device_name, "show ip interface brief")
    return output


async def get_routing_table_live(device_name: str) -> str:
    """Get routing table from a real device."""
    output = await send_command_to_device(device_name, "show ip route")
    return f"Routing Table for {device_name}:\n{output}"


async def ping_from_device(device_name: str, target: str) -> str:
    """Ping a target from a device."""
    output = await send_command_to_device(device_name, f"ping {target} repeat 3")
    return output


async def get_running_config(device_name: str, section: str = None) -> str:
    """Get running config from a device."""
    if section:
        output = await send_command_to_device(device_name, f"show running-config | section {section}")
    else:
        output = await send_command_to_device(device_name, "show running-config")
    return output


# ===== TOOL REGISTRY =====

TOOLS = {
    "health_check": check_device_health,
    "ospf_neighbors": get_ospf_neighbors_live,
    "bgp_summary": get_bgp_summary_live,
    "interface_status": get_interface_status_live,
    "routing_table": get_routing_table_live,
    "ping": ping_from_device,
    "running_config": get_running_config,
    "send_command": send_command_to_device,
}

TOOL_DESCRIPTIONS = """Available tools:
1. health_check - Check device health. Input: device name (e.g., "R1")
2. ospf_neighbors - Get OSPF neighbors. Input: device name (e.g., "R1")
3. bgp_summary - Get BGP summary. Input: device name (e.g., "R1")
4. interface_status - Get interface status. Input: device name, optionally interface (e.g., "R1" or "R1,GigabitEthernet1")
5. routing_table - Get routing table. Input: device name (e.g., "R1")
6. ping - Ping from a device. Input: device,target (e.g., "R1,8.8.8.8")
7. running_config - Get running config. Input: device name, optionally section (e.g., "R1" or "R1,router ospf")
8. send_command - Send any command. Input: device,command (e.g., "R1,show version")

Available devices: R1, R2, R3, R4, Switch-R1, Switch-R2, Switch-R4, Alpine-1"""


# ===== RAG SETUP =====

def search_documentation(query: str, k: int = 2) -> str:
    """Search network documentation for relevant information."""
    try:
        from rag_setup import get_vector_store
        vector_store = get_vector_store()
        results = vector_store.similarity_search(query, k=k)
        if results:
            return "\n\n".join([doc.page_content for doc in results])
        return "No relevant documentation found."
    except Exception as e:
        return f"Documentation search unavailable: {str(e)}"


# ===== CHATBOT =====

class LiveNetworkChatbot:
    """Interactive network assistant connected to real lab devices."""

    def __init__(self, model: str = MODEL_NAME):
        self.llm = OllamaLLM(model=model)
        self.model_name = model
        self.chat_history = []

        self.router_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a network engineering assistant connected to a LIVE network lab.

{TOOL_DESCRIPTIONS}

Based on the user's question, respond with EXACTLY ONE of these formats:

For device queries, respond:
ACTION: TOOL
TOOL_NAME: <tool_name>
TOOL_INPUT: <input_value>

For troubleshooting procedures or "how to" questions, respond:
ACTION: DOCS
QUERY: <search_terms>

For direct answers, respond:
ACTION: DIRECT
ANSWER: <your_answer>

Important:
- These are REAL devices - commands will actually execute
- Pick only ONE action
- For tools needing two inputs, separate with comma (e.g., "R1,GigabitEthernet1")
- Match tool names exactly as listed"""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])

        self.response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful network engineering assistant analyzing REAL device output.
Provide concise, technical analysis of the data.
Highlight any issues or anomalies you see.
If the output shows errors or problems, explain what they mean."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", """Question: {question}

Live Device Output:
{context}

Analysis:""")
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

    async def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        """Execute a tool and return the result."""
        if tool_name not in TOOLS:
            return f"Unknown tool: {tool_name}. Available: {', '.join(TOOLS.keys())}"

        try:
            # Parse input - some tools need two arguments
            if "," in tool_input:
                parts = [p.strip() for p in tool_input.split(",", 1)]
                if tool_name in ["ping", "send_command"]:
                    return await TOOLS[tool_name](parts[0], parts[1])
                elif tool_name == "interface_status":
                    return await TOOLS[tool_name](parts[0], parts[1] if len(parts) > 1 else None)
                elif tool_name == "running_config":
                    return await TOOLS[tool_name](parts[0], parts[1] if len(parts) > 1 else None)

            # Single argument tools
            return await TOOLS[tool_name](tool_input)
        except Exception as e:
            return f"Tool error: {str(e)}"

    async def chat(self, question: str, verbose: bool = True) -> str:
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
                print(f"  [Executing: {tool_name}({tool_input})]")
            context = await self._execute_tool(tool_name, tool_input)

        elif action == "DOCS":
            query = parsed.get("query", question)
            if verbose:
                print(f"  [Searching docs: {query}]")
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


async def main():
    """Run the interactive chatbot."""
    print("=" * 60)
    print("NETWORK ENGINEERING ASSISTANT - LIVE LAB")
    print(f"Model: {MODEL_NAME}")
    print("=" * 60)
    print("\n⚠️  CONNECTED TO REAL DEVICES - Commands will execute!")
    print(f"\nAvailable devices: {', '.join(DEVICES.keys())}")
    print("\nCapabilities:")
    print("  • Health checks, OSPF, BGP, interfaces, routing")
    print("  • Send any command to any device")
    print("  • Troubleshooting guidance from documentation")
    print("\nCommands: 'quit' to exit, 'clear' to reset history")
    print("=" * 60)

    chatbot = LiveNetworkChatbot()

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

        response = await chatbot.chat(user_input)
        print(f"\nAssistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())