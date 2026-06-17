import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore  # <--- UPDATED IMPORT HERE
from qdrant_client import QdrantClient

# Load keys from hidden .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

def run_rag_ingestion():
    print("Starting Cloud-Ready RAG Ingestion Pipeline...")
    
    # 1. Load document
    current_dir = os.path.dirname(__file__)
    doc_path = os.path.join(current_dir, "documents", "city_policy_manual.txt")
    loader = TextLoader(doc_path)
    documents = loader.load()

    # 2. Chunk document
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    # 3. Initialize Embeddings
    print("Initializing embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Connect directly to Qdrant Cloud
    print(f"Connecting to Qdrant Cloud Cluster...")
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

    # 5. Store chunks + vectors directly into Cloud Vector DB
    # We use QdrantVectorStore now instead of Qdrant
    qdrant = QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name="city_policies",
        force_recreate=True
    )
    
    print("Success! Your city policies are now securely indexed in Qdrant Cloud!")

if __name__ == "__main__":
    run_rag_ingestion()