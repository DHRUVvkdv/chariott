from typing import List, Dict
from pinecone import Pinecone
from core.config import settings

# Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# Get the index
index = pc.Index(settings.PINECONE_INDEX_NAME)


async def store_embeddings(
    document_id: str, embeddings: List[List[float]], metadata: Dict[str, str]
):
    vectors = []
    for i, embedding in enumerate(embeddings):
        vectors.append((f"{document_id}_{i}", embedding, metadata))

    index.upsert(vectors=vectors)


async def query_embeddings(query_vector: List[float], top_k: int = 5):
    results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    return results
