import json
import boto3
from typing import List

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",  # replace with your preferred region
)


async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    embeddings = []
    for text in texts:
        body = json.dumps({"inputText": text})
        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        response_body = json.loads(response["body"].read())
        embeddings.append(response_body["embedding"])
    return embeddings
