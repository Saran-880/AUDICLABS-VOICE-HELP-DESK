
import logging
from pathlib import Path
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.retrievers import BM25Retriever


from langchain_classic.retrievers import EnsembleRetriever


# --------------------------------------------------
# Configuration
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
CHROMA_DIR = ROOT_DIR / "data" / "chroma"

COLLECTION_NAME = "audiclabs_docs"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 8
BM25_WEIGHT = 0.5
SEMANTIC_WEIGHT = 0.5

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Semantic retriever using existing ChromaDB
# --------------------------------------------------

class ChromaSemanticRetriever(BaseRetriever):
    """Retrieve relevant document chunks using embeddings."""

    collection: Any
    embedding_model: Any
    k: int = 4

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager,
    ) -> list[Document]:

        query_embedding = self.embedding_model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.k,
            include=["documents", "metadatas", "distances"],
        )

        documents = []

        result_documents = results["documents"][0]
        result_metadatas = results["metadatas"][0]

        for text, metadata in zip(
            result_documents,
            result_metadatas,
        ):
            if not text or not text.strip():
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata=metadata or {},
                )
            )

        return documents


# --------------------------------------------------
# Load indexed documents for BM25
# --------------------------------------------------

def load_documents(collection) -> list[Document]:
    """Load indexed chunks from ChromaDB without re-embedding."""

    data = collection.get(
        include=["documents", "metadatas"],
    )

    documents = []

    for text, metadata in zip(
        data["documents"],
        data["metadatas"],
    ):
        if not text or not text.strip():
            continue

        documents.append(
            Document(
                page_content=text,
                metadata=metadata or {},
            )
        )

    if not documents:
        raise RuntimeError(
            "No indexed documents found. "
            "Run scripts/ingest_docs.py first."
        )

    return documents


# --------------------------------------------------
# Build all three retrieval methods
# --------------------------------------------------

def build_retrievers():
    """Build BM25, semantic, and hybrid retrievers."""

    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"Chroma database not found: {CHROMA_DIR}\n"
            "Run scripts/ingest_docs.py first."
        )

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
    )

    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Could not find Chroma collection "
            f"'{COLLECTION_NAME}'. Run ingestion first."
        ) from exc

    logger.info(
        "Indexed chunks in ChromaDB: %d",
        collection.count(),
    )

    # Load chunks for keyword search.
    documents = load_documents(collection)

    logger.info(
        "Loaded %d documents for BM25.",
        len(documents),
    )

    # 1. BM25 keyword retriever.
    bm25 = BM25Retriever.from_documents(documents)
    bm25.k = TOP_K

    # 2. Semantic retriever using local embeddings.
    logger.info("Loading local embedding model: %s", EMBEDDING_MODEL)

    model = SentenceTransformer(EMBEDDING_MODEL)

    semantic = ChromaSemanticRetriever(
        collection=collection,
        embedding_model=model,
        k=TOP_K,
    )

    # 3. Hybrid retriever combines both ranked lists.
    hybrid = EnsembleRetriever(
        retrievers=[bm25, semantic],
        weights=[BM25_WEIGHT, SEMANTIC_WEIGHT],
    )

    return bm25, semantic, hybrid


# --------------------------------------------------
# Print retrieval results
# --------------------------------------------------

def print_results(
    method_name: str,
    documents: list[Document],
) -> None:

    print(f"\n--- {method_name} ---")

    if not documents:
        print("No documents returned.")
        return

    for rank, document in enumerate(documents, start=1):
        metadata = document.metadata

        title = metadata.get("title", "Unknown")
        url = metadata.get("url", "Missing")
        content = " ".join(
            document.page_content.split()
        )

        print(f"\nRank: {rank}")
        print(f"Title: {title}")
        print(f"URL: {url}")
        print(f"Text: {content[:300]}")


# --------------------------------------------------
# Test retrieval methods independently
# --------------------------------------------------

def main():

    bm25, semantic, hybrid = build_retrievers()

    questions = [
        "Where in the AudicLabs console can I create an API key?",
        "How many credits does a new account start with?",
        "What is the AudicLabs STT streaming endpoint?",
        "How do I generate speech using the text to speech API?",
        "What do HTTP 401, 402, 429, and 503 errors mean?",
    ]

    for question in questions:

        print("\n" + "=" * 85)
        print(f"QUESTION: {question}")
        print("=" * 85)

        # BM25 keyword results.
        bm25_results = bm25.invoke(question)
        print_results(
            "BM25 KEYWORD SEARCH",
            bm25_results[:3],
        )

        # Semantic embedding results.
        semantic_results = semantic.invoke(question)
        print_results(
            "SEMANTIC SEARCH",
            semantic_results[:3],
        )

        # Combined results.
        hybrid_results = hybrid.invoke(question)
        print_results(
            "HYBRID SEARCH (BM25 + SEMANTIC)",
            hybrid_results[:3],
        )


if __name__ == "__main__":
    main()
