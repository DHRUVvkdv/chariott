from typing import List, Dict
from pinecone import Pinecone
from core.config import settings

# Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# Get the index
index = pc.Index(settings.PINECONE_INDEX_NAME)


async def store_embeddings(
    document_id: str,
    embeddings: List[List[float]],
    metadata: Dict[str, str],
    texts: List[str],  # Add this parameter to receive the actual text chunks
):
    vectors = []
    for i, (embedding, text) in enumerate(zip(embeddings, texts)):
        vector_metadata = metadata.copy()
        vector_metadata["text"] = text  # Store the actual text content
        vectors.append((f"{document_id}_{i}", embedding, vector_metadata))

    index.upsert(vectors=vectors)


async def query_embeddings(query_vector: List[float], top_k: int = 5):
    results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    return results


async def delete_document_vectors(document_id: str):
    # First, query to get all vector IDs associated with the document
    results = index.query(
        vector=[0] * 1536,  # dummy vector, adjust dimension if needed
        filter={"document_id": document_id},
        top_k=10000,  # adjust based on your maximum expected vectors per document
        include_metadata=False,
    )

    # Extract the vector IDs
    vector_ids = [match.id for match in results.matches]

    # Delete the vectors by their IDs
    if vector_ids:
        delete_response = index.delete(ids=vector_ids)
        return f"Deleted {len(vector_ids)} vectors for document {document_id}"
    else:
        return f"No vectors found for document {document_id}"
