"""Adding memory to conversations with LangChain and Ollama.

This version uses RunnableWithMessageHistory for automatic history management.
"""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Initialize model
llm = OllamaLLM(model="llama3.2")

# Create prompt with a placeholder for chat history
# (This stays exactly the same as your original!)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful network engineering assistant. Be concise."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

# Create base chain (same as before)
chain = prompt | llm

# --- NEW: Session-based history management ---

# Store holds ChatMessageHistory objects keyed by session_id
# In production, this could be Redis, a database, etc.
store = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    """Retrieve or create a ChatMessageHistory for the given session.

    This function is called by RunnableWithMessageHistory each time
    you invoke the chain. It's how the wrapper knows where to store
    and retrieve conversation history.
    """
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


# Wrap the chain with automatic history management
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",   # Maps to {question} in your prompt
    history_messages_key="history"   # Maps to MessagesPlaceholder(variable_name="history")
)


def chat(question: str, session_id: str = "default") -> str:
    """Send a message - history is managed automatically!

    Notice: No more manual appending of HumanMessage/AIMessage.
    The wrapper handles it for us.
    """
    response = chain_with_history.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}}
    )
    return response


# Have a conversation (using default session)
print("Q: What is OSPF?")
print(f"A: {chat('What is OSPF?')}\n")

print("Q: What are its main area types?")
print(f"A: {chat('What are its main area types?')}\n")

print("Q: Which one would I use for a stub network?")
print(f"A: {chat('Which one would I use for a stub network?')}\n")

# Bonus: Demonstrate multiple sessions
print("=" * 50)
print("Starting a NEW session (different user):")
print("=" * 50 + "\n")

print("Q: What is BGP?")
print(f"A: {chat('What is BGP?', session_id='user2')}\n")

# This question in session 'user2' won't know about OSPF from the default session
print("Q: What did we discuss earlier?")
print(f"A: {chat('What did we discuss earlier?', session_id='user2')}\n")
