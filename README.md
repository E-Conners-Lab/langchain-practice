# LangChain Practice

A collection of LangChain examples using Ollama and Llama 3.2, with a focus on network engineering use cases.

## Prerequisites

- Python 3.12.12 (3.14 has compatibility issues with some dependencies)
- [Ollama](https://ollama.ai/) installed and running
- Llama 3.2 model pulled (`ollama pull llama3.2`)

## Installation

```bash
pip install -r requirements.txt
```

## Examples

### Basics

| File | Concept | Description |
|------|---------|-------------|
| `basic_prompt.py` | Direct invocation | Simple `llm.invoke()` call |
| `prompt_templates.py` | PromptTemplate | Dynamic prompts with variables |
| `basic_chain.py` | LCEL chains | Pipe operator with output parsers |

### Prompting Techniques

| File | Concept | Description |
|------|---------|-------------|
| `chat_prompts.py` | ChatPromptTemplate | System/human message roles |
| `few_shot.py` | Few-shot learning | Teaching via examples |

### Memory & State

| File | Concept | Description |
|------|---------|-------------|
| `memory_chat.py` | Conversation memory | `RunnableWithMessageHistory` for session-based chat |

### Chains & Agents

| File | Concept | Description |
|------|---------|-------------|
| `sequential_chains.py` | Sequential chains | Output of one chain feeds into the next |
| `custom_tools.py` | Custom tools | 9 network tools: subnet calc, VLAN lookup, ping, routing, OSPF, BGP, ACL |
| `react_agent.py` | Tool-using agent | LLM decides which tool to call |

### RAG (Retrieval-Augmented Generation)

| File | Concept | Description |
|------|---------|-------------|
| `rag_setup.py` | Vector store setup | ChromaDB with HuggingFace embeddings |
| `rag_chain.py` | RAG chain | Query network docs with context retrieval |
| `docs/network_runbook.md` | Knowledge base | OSPF, BGP, VLAN, interface troubleshooting guides |

### Network Chatbots

| File | Concept | Description |
|------|---------|-------------|
| `network_chatbot.py` | Integrated chatbot | Combines tools, RAG, and conversation memory with simulated data |
| `network_chatbot_live.py` | Live lab chatbot | Connects to real devices via Scrapli for live network queries |

## Usage

Make sure Ollama is running, then execute any example:

```bash
python basic_prompt.py
python memory_chat.py
python sequential_chains.py
python react_agent.py

# RAG - first build the vector store, then query
python rag_setup.py
python rag_chain.py

# Network chatbots - interactive assistants
python network_chatbot.py       # Uses simulated data
python network_chatbot_live.py  # Connects to real lab devices (requires .env config)
```

## Topics Covered

- BGP/OSPF troubleshooting
- Cisco IOS commands
- Subnet calculations
- VLAN lookups
- Inter-VLAN routing diagnostics
