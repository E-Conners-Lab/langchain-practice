# LangChain Practice

A collection of LangChain examples using Ollama and Llama 3.2, with a focus on network engineering use cases.

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Llama 3.2 model pulled (`ollama pull llama3.2`)

## Installation

```bash
pip install langchain-ollama langchain-core
```

## Examples

### Basic Prompt (`basic_prompt.py`)
Simple LLM invocation demonstrating direct model interaction.

### Prompt Templates (`prompt_templates.py`)
Using `PromptTemplate` with input variables for dynamic prompt generation.

### Basic Chain (`basic_chain.py`)
Demonstrates LangChain Expression Language (LCEL) to create chains with prompt templates and output parsers.

### Chat Prompts (`chat_prompts.py`)
Using `ChatPromptTemplate` with system and human messages to create a network engineering assistant.

### Few-Shot Prompting (`few_shot.py`)
Implements few-shot learning with `FewShotPromptTemplate` to teach the model Cisco command descriptions.

## Usage

Make sure Ollama is running, then execute any example:

```bash
python basic_prompt.py
python basic_chain.py
python chat_prompts.py
python few_shot.py
python prompt_templates.py
```

## Topics Covered

- BGP troubleshooting
- OSPF neighbor states
- Cisco IOS commands
- Network protocol explanations
