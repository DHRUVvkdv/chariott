import boto3
from typing import List
from core.config import settings
import json

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=settings.PRIVATE_AWS_REGION,
)


async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    embeddings = []
    for text in texts:
        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": text}),
        )
        embedding = json.loads(response["body"].read())["embedding"]
        embeddings.append(embedding)
    return embeddings
