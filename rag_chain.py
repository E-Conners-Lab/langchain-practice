"""RAG chain for answering question from network documentation."""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from rag_setup import get_vector_store

def format_docs(docs):
    """Format retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


# Initialize components
llm = OllamaLLM(model="llama3.2")
vector_store = get_vector_store()
retriever = vector_store.as_retriever(search_kwargd={"k": 3})

# RAG prompt
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a network engineering assistant. Answer questions based on the provided documentation context.
If the context doesn't contain relevant information, say so and provide general guidance.
Be concise and technical."""),
    ("human", """Context from documentation:
{context}
    
Question: {question}
Answer:""")
])

# Build the RAG chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

def ask(question: str) -> str:
    """Ask a question using RAG."""
    return rag_chain.invoke(question)

if  __name__ == "__main__":
    print("Network Documentation RAG")
    print("=" * 50)

    questions = [
        "How do I troubleshoot OSPF stuck in EXSTART state?",
        "What causes high CRC errors on an interface?",
        "Why might BGP not advertise a route?",
        "WHat should I check if users can't reach other VLANs?",
    ]

    for question in questions:
        print(f"\nQ: {question}")
        print("-" * 40)
        answer = ask(question)
        print(f"A: {answer}")
        print("\n" + "=" * 50)