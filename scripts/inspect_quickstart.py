
import chromadb

client = chromadb.PersistentClient(path="data/chroma")
collection = client.get_collection("audiclabs_docs")

results = collection.get(
    where={"url": "https://docs.audiclabs.com/docs/quickstart"},
    include=["documents", "metadatas"],
)

print("Quickstart chunks:", len(results["documents"]))

for i, (document, metadata) in enumerate(
    zip(results["documents"], results["metadatas"]),
    start=1,
):
    print(f"\n--- Chunk {i} ---")
    print("Title:", metadata.get("title"))
    print("URL:", metadata.get("url"))
    print(document[:1000])
