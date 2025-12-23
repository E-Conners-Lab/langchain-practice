"""RAG setup for network documentation."""

from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
# Paths
DOCS_PATH = Path("docs")
CHROMA_PATH = Path("chroma_db")


def load_documents():
    """Load all documents from the docs folder."""
    loader = DirectoryLoader(
        str(DOCS_PATH),
        glob="**/*.md",
        loader_cls=TextLoader
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")
    return documents


def split_documents(documents):
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def create_vector_store(chunks):
    """Create ChromaDB vector store from document chunks."""
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_PATH)
    )
    print(f"Created vector store at {CHROMA_PATH}")
    return vector_store


def get_vector_store():
    """Load existing vector store."""
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    return Chroma(
        persist_directory=str(CHROMA_PATH),
        embedding_function=embeddings
    )


if __name__ == "__main__":
    print("Building RAG Vector Store")
    print("=" * 50)

    docs = load_documents()
    chunks = split_documents(docs)

    print("\nSample chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i + 1} ---")
        print(chunk.page_content[:200] + "...")

    vector_store = create_vector_store(chunks)

    print("\n" + "=" * 50)
    print("Testing retrieval...")
    results = vector_store.similarity_search("OSPF stuck in EXSTART", k=2)
    print(f"\nQuery: 'OSPF stuck in EXSTART'")
    print(f"Found {len(results)} relevant chunks:")
    for i, doc in enumerate(results):
        print(f"\n--- Result {i + 1} ---")
        print(doc.page_content)