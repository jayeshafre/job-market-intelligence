"""
api/core/rag_pipeline.py
========================
RAG Pipeline — Phase 6.

Responsibilities:
  1. Load and chunk documents from data/rag_documents/
  2. Generate embeddings using sentence-transformers (local, free)
  3. Store embeddings in ChromaDB (local vector database)
  4. Retrieve the most relevant chunks for a user query
  5. Format retrieved chunks for prompt injection

Why ChromaDB?
  - Runs entirely locally — no external service, no API key, no cost
  - Persistent storage — index once, query forever
  - Simple Python API — no infrastructure setup needed
  - Used in production by many startups for exactly this use case

Why sentence-transformers?
  - Free, open-source embedding model
  - all-MiniLM-L6-v2 is fast, small (90MB), and accurate enough for
    domain-specific retrieval like workforce analytics
  - No OpenAI API calls = zero embedding cost

Key concepts:
  Embedding  = converting text into a vector of numbers (384 dimensions)
               that captures semantic meaning. Similar texts → similar vectors.
  Similarity = cosine similarity between query vector and stored vectors
               finds the most semantically relevant chunks.
  Chunk      = a piece of a document (we use paragraph-level chunks)
               Small enough to be specific, large enough to be meaningful.

Place this file at: backend/api/core/rag_pipeline.py
"""

import logging
import os
from pathlib import Path
from functools import lru_cache

logger = logging.getLogger(__name__)

# ChromaDB and sentence-transformers are imported lazily inside functions
# so the app still starts even if they're not installed yet.
# This gives a clean "not installed" error instead of an import crash.

# =============================================================================
# CONFIGURATION
# =============================================================================

# Path to your RAG documents folder
# Adjust this path if your project root is different
RAG_DOCS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "rag_documents"

# ChromaDB persistent storage location
CHROMA_DB_DIR = Path(__file__).parent.parent.parent / "data" / "chroma_db"

# Collection name inside ChromaDB
COLLECTION_NAME = "job_market_intelligence"

# Embedding model — downloads ~90MB on first use, then cached locally
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Number of document chunks to retrieve per query
TOP_K_RESULTS = 3


# =============================================================================
# EMBEDDING MODEL (singleton)
# =============================================================================

@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Loads the sentence-transformer embedding model once and caches it.

    Why lru_cache?
      The model is ~90MB and takes 2-3 seconds to load.
      Loading it once at startup and reusing it is the same pattern
      as your Groq client singleton — one load, many uses.

    Returns:
        SentenceTransformer model instance.
    """
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"[RAG] Loading embedding model: {EMBEDDING_MODEL}")
        model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("[RAG] Embedding model loaded successfully.")
        return model
    except ImportError:
        raise RuntimeError(
            "sentence-transformers not installed. "
            "Run: pip install sentence-transformers==2.7.0"
        )


# =============================================================================
# CHROMADB CLIENT (singleton)
# =============================================================================

@lru_cache(maxsize=1)
def get_chroma_client():
    """
    Creates a persistent ChromaDB client.
    Data is stored on disk at CHROMA_DB_DIR — survives restarts.
    """
    try:
        import chromadb
        from chromadb.config import Settings

        CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

        client = chromadb.PersistentClient(
            path=str(CHROMA_DB_DIR),
            settings=Settings(
                anonymized_telemetry=False
            )
        )

        logger.info(f"[RAG] ChromaDB client initialized at {CHROMA_DB_DIR}")
        return client

    except ImportError:
        raise RuntimeError(
            "chromadb not installed. Run: pip install chromadb==0.4.22"
        )


def get_or_create_collection():
    """
    Gets the ChromaDB collection, creating it if it doesn't exist.
    The collection is where all document vectors are stored.
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity for semantic search
    )
    return collection


# =============================================================================
# DOCUMENT LOADER & CHUNKER
# =============================================================================

def load_documents() -> list[dict]:
    """
    Loads all .txt files from the RAG documents directory.

    Returns:
        List of dicts with keys: doc_id, filename, content, chunks
    """
    if not RAG_DOCS_DIR.exists():
        logger.warning(f"[RAG] Documents directory not found: {RAG_DOCS_DIR}")
        return []

    documents = []
    for txt_file in RAG_DOCS_DIR.glob("*.txt"):
        try:
            content = txt_file.read_text(encoding="utf-8").strip()
            if content:
                documents.append({
                    "doc_id":   txt_file.stem,
                    "filename": txt_file.name,
                    "content":  content,
                })
                logger.info(f"[RAG] Loaded document: {txt_file.name}")
        except Exception as e:
            logger.warning(f"[RAG] Failed to load {txt_file.name}: {e}")

    return documents


def chunk_document(doc_id: str, content: str, chunk_size: int = 300) -> list[dict]:
    """
    Splits a document into overlapping chunks for indexing.

    Why chunk?
      LLMs have token limits. You can't inject an entire document.
      Chunking splits it into pieces — each piece is indexed separately.
      At query time, only the MOST RELEVANT pieces are retrieved.

    Why overlap?
      Overlap between chunks (50 words) prevents losing context at boundaries.
      If a key sentence spans a chunk boundary, overlap ensures it's captured.

    Args:
        doc_id:     Unique document identifier.
        content:    Full document text.
        chunk_size: Approximate words per chunk.

    Returns:
        List of chunk dicts with id, text, doc_id, chunk_index.
    """
    words  = content.split()
    overlap = 50  # words of overlap between chunks
    chunks  = []
    i       = 0
    idx     = 0

    while i < len(words):
        chunk_words = words[i : i + chunk_size]
        chunk_text  = " ".join(chunk_words)
        chunks.append({
            "id":          f"{doc_id}_chunk_{idx}",
            "text":        chunk_text,
            "doc_id":      doc_id,
            "chunk_index": idx,
        })
        i   += chunk_size - overlap
        idx += 1

    return chunks


# =============================================================================
# INDEXING
# =============================================================================

def index_documents(force_reindex: bool = False) -> dict:
    """
    Loads documents, generates embeddings, stores in ChromaDB.

    This is the "offline" step — run once (or when documents change).
    In production this would be triggered by a document upload event.

    Args:
        force_reindex: If True, clears existing collection and reindexes.

    Returns:
        dict with status, documents_indexed, chunks_indexed.
    """
    collection   = get_or_create_collection()
    embed_model  = get_embedding_model()

    # Check if already indexed
    existing_count = collection.count()
    if existing_count > 0 and not force_reindex:
        logger.info(f"[RAG] Collection already has {existing_count} chunks. Skipping reindex.")
        return {
            "status":           "already_indexed",
            "chunks_in_store":  existing_count,
            "documents_indexed": 0,
            "chunks_indexed":    0,
        }

    if force_reindex and existing_count > 0:
        # Delete and recreate the collection
        client = get_chroma_client()
        client.delete_collection(COLLECTION_NAME)
        logger.info("[RAG] Cleared existing collection for reindex.")
        collection = get_or_create_collection()

    documents = load_documents()
    if not documents:
        return {
            "status":            "no_documents",
            "documents_indexed": 0,
            "chunks_indexed":    0,
        }

    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc["doc_id"], doc["content"])
        all_chunks.extend(chunks)

    # Generate embeddings for all chunks at once (batch = fast)
    texts = [c["text"] for c in all_chunks]
    logger.info(f"[RAG] Generating embeddings for {len(texts)} chunks...")
    embeddings = embed_model.encode(texts, show_progress_bar=False).tolist()

    # Store in ChromaDB
    collection.add(
        ids        = [c["id"] for c in all_chunks],
        embeddings = embeddings,
        documents  = texts,
        metadatas  = [{"doc_id": c["doc_id"], "chunk_index": c["chunk_index"]} for c in all_chunks],
    )

    logger.info(f"[RAG] Indexed {len(documents)} documents, {len(all_chunks)} chunks.")
    return {
        "status":            "indexed",
        "documents_indexed": len(documents),
        "chunks_indexed":    len(all_chunks),
    }


# =============================================================================
# RETRIEVAL
# =============================================================================

def retrieve_relevant_chunks(query: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
    """
    Finds the most semantically relevant document chunks for a query.

    How it works:
      1. Embed the query using the same model used during indexing
      2. ChromaDB computes cosine similarity between query vector
         and all stored chunk vectors
      3. Returns the top_k most similar chunks

    This is the core of RAG — semantic search, not keyword search.
    "Which jobs are safest?" retrieves chunks about future-safe careers
    even if the exact phrase isn't in the documents.

    Args:
        query:  The user's question.
        top_k:  Number of chunks to retrieve.

    Returns:
        List of dicts with text, doc_id, similarity_score.
    """
    collection  = get_or_create_collection()
    embed_model = get_embedding_model()

    # Check collection is populated
    if collection.count() == 0:
        logger.warning("[RAG] Collection is empty. Run /rag/index first.")
        return []

    # Embed the query
    query_embedding = embed_model.encode([query], show_progress_bar=False).tolist()[0]

    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    if results and results["documents"]:
        for i, (text, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )):
            # Convert distance to similarity score (cosine: distance 0 = perfect match)
            similarity = round(1 - dist, 4)
            chunks.append({
                "text":       text,
                "doc_id":     meta.get("doc_id", "unknown"),
                "chunk_index": meta.get("chunk_index", 0),
                "similarity": similarity,
            })

    logger.info(f"[RAG] Retrieved {len(chunks)} chunks for query (top similarity: "
                f"{chunks[0]['similarity'] if chunks else 'N/A'})")
    return chunks


# =============================================================================
# CONTEXT FORMATTER
# =============================================================================

def format_rag_context(chunks: list[dict]) -> str:
    """
    Formats retrieved chunks into a readable text block for prompt injection.
    Similar to format_snapshot_for_prompt() in executive_summary.py.
    """
    if not chunks:
        return ""

    lines = ["=== RETRIEVED KNOWLEDGE BASE CONTEXT ===\n"]
    for i, chunk in enumerate(chunks, start=1):
        lines.append(
            f"[Document {i} | Source: {chunk['doc_id']} | "
            f"Relevance: {chunk['similarity']:.2f}]"
        )
        lines.append(chunk["text"])
        lines.append("")  # blank line between chunks

    lines.append(
        "Use the above retrieved context alongside the platform KPI data "
        "to give a comprehensive, well-grounded answer."
    )
    return "\n".join(lines)