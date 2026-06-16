# tools/vector_store.py
import chromadb
from chromadb.utils import embedding_functions

# Use a local persistent store — saves to disk automatically
client = chromadb.PersistentClient(path="./chroma_db")

# Use the default embedding function (no extra API key needed)
ef = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="research_results",
    embedding_function=ef
)

def save_to_store(content: str, metadata: dict, doc_id: str) -> bool:
    """
    Save a piece of content to the vector store.
    metadata should include source url, agent name, etc.
    """
    try:
        collection.upsert(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        return True
    except Exception as e:
        print(f"Vector store save error: {e}")
        return False

def search_store(query: str, n_results: int = 3) -> list[dict]:
    """
    Semantic search across everything saved in the store.
    Returns the most relevant chunks for a given query.
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )

        output = []
        for i, doc in enumerate(results["documents"][0]):
            output.append({
                "content": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        return output

    except Exception as e:
        print(f"Vector store search error: {e}")
        return []

def clear_store() -> bool:
    """Clear all results — call this at the start of each new research query."""
    try:
        client.delete_collection("research_results")
        global collection
        collection = client.get_or_create_collection(
            name="research_results",
            embedding_function=ef
        )
        return True
    except Exception as e:
        print(f"Clear store error: {e}")
        return False