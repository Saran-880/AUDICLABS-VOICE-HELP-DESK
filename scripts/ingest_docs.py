
import json
import logging
import hashlib
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. Project configuration
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "data" / "docs"
CHROMA_DIR = ROOT_DIR / "data" / "chroma"
MANIFEST_PATH = DOCS_DIR / "manifest.json"

COLLECTION_NAME = "audiclabs_docs"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
BATCH_SIZE = 64

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# 2. Load manifest
# --------------------------------------------------

def load_manifest():
    """Load document filenames, titles, and source URLs."""

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Manifest not found: {MANIFEST_PATH}"
        )

    with MANIFEST_PATH.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(
            "Expected manifest.json to contain a list of records."
        )

    manifest = {}

    for record in records:
        if not isinstance(record, dict):
            continue

        filename = record.get("filename")

        if filename:
            manifest[filename] = record

    if not manifest:
        raise ValueError(
            "No valid document records found in manifest.json."
        )

    logger.info("Manifest records loaded: %d", len(manifest))

    return manifest


# --------------------------------------------------
# 3. Read downloaded documents
# --------------------------------------------------

def load_document(path, metadata):
    """Read a downloaded Markdown document."""

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        ).strip()

    except OSError as exc:
        logger.warning(
            "Could not read %s: %s",
            path.name,
            exc,
        )
        return None

    title = metadata.get("title") or path.stem.replace("_", " ")
    source_url = metadata.get("url", "")

    if len(text) < 50:
        logger.warning(
            "Skipping short document: %s",
            path.name,
        )
        return None

    if not source_url:
        logger.warning(
            "Missing source URL for %s",
            path.name,
        )

    return {
        "text": text,
        "title": title,
        "url": source_url,
        "filename": path.name,
    }


# --------------------------------------------------
# 4. Split documents into chunks
# --------------------------------------------------

def create_chunks(documents):
    """Split text while preserving citation metadata."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )

    chunks = []

    for document in documents:
        pieces = splitter.create_documents(
            [document["text"]],
            metadatas=[{
                "title": document["title"],
                "url": document["url"],
                "filename": document["filename"],
            }],
        )

        for piece in pieces:
            chunk_text = piece.page_content.strip()

            # Ignore chunks containing only a title or source URL.
            meaningful_text = chunk_text.replace(
                f"# {document['title']}",
                "",
            ).replace(
                f"Source URL: {document['url']}",
                "",
            ).strip()

            if len(meaningful_text) < 80:
                continue

            metadata = dict(piece.metadata)

            metadata["start_index"] = int(
                metadata.get("start_index", 0)
            )

            chunks.append({
                "text": chunk_text,
                "metadata": metadata,
            })

    return chunks


# --------------------------------------------------
# 5. Create and populate ChromaDB
# --------------------------------------------------

def main():
    if not DOCS_DIR.exists():
        raise SystemExit(
            f"Documents folder not found: {DOCS_DIR}"
        )

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest = load_manifest()
    documents = []

    # Read files listed by the downloader only.
    for filename, metadata in sorted(manifest.items()):
        path = DOCS_DIR / filename

        if not path.is_file():
            logger.warning(
                "Manifest file is missing: %s",
                filename,
            )
            continue

        document = load_document(path, metadata)

        if document:
            documents.append(document)

    if not documents:
        raise SystemExit("No usable documents found.")

    chunks = create_chunks(documents)

    if not chunks:
        raise SystemExit("No meaningful chunks were generated.")

    logger.info("Documents loaded: %d", len(documents))
    logger.info("Chunks generated: %d", len(chunks))

    # Load the local embedding model.
    logger.info(
        "Loading embedding model: %s",
        EMBEDDING_MODEL,
    )

    model = SentenceTransformer(EMBEDDING_MODEL)

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    # Rebuild only our own collection.
    # Other collections in this database are untouched.
    try:
        client.delete_collection(
            name=COLLECTION_NAME
        )
        logger.info(
            "Deleted previous collection: %s",
            COLLECTION_NAME,
        )

    except Exception:
        logger.info(
            "No previous collection found; creating a new one."
        )

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Generate embeddings in batches.
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]

        texts = [
            item["text"]
            for item in batch
        ]

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        ids = []

        for index, item in enumerate(batch):
            identity = (
                f"{item['metadata']['filename']}:"
                f"{item['metadata']['start_index']}:"
                f"{start + index}"
            )

            digest = hashlib.sha256(
                identity.encode("utf-8")
            ).hexdigest()

            ids.append(digest)

        collection.add(
            ids=ids,
            documents=texts,
            metadatas=[
                item["metadata"]
                for item in batch
            ],
            embeddings=embeddings,
        )

        logger.info(
            "Indexed %d/%d chunks",
            start + len(batch),
            len(chunks),
        )

    logger.info("Ingestion completed successfully.")
    logger.info("Collection: %s", COLLECTION_NAME)
    logger.info("Documents loaded: %d", len(documents))
    logger.info("Chunks stored: %d", collection.count())
    logger.info("Chroma directory: %s", CHROMA_DIR)


if __name__ == "__main__":
    main()
