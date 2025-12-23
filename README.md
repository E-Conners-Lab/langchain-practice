# LangChain Practice

A collection of LangChain examples using Ollama and Llama 3.2, with a focus on network engineering use cases.

## Prerequisites

- Python 3.8+
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

## Usage

Make sure Ollama is running, then execute any example:

```bash
python basic_prompt.py
python memory_chat.py
python sequential_chains.py
python react_agent.py
```

## Topics Covered

- BGP/OSPF troubleshooting
- Cisco IOS commands
- Subnet calculations
- VLAN lookups
- Inter-VLAN routing diagnostics
