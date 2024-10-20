import json
import boto3
import os
from typing import List
from services.pinecone_service import query_embeddings
from botocore.exceptions import ClientError
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from fastapi import HTTPException
from core.config import settings


class RAGService:
    """
    A class providing RAG (Retrieve, Augment, Generate) functionality.
    """

    def __init__(self):
        """
        Initializes the RAGService with AWS credentials and model IDs.
        """
        self.bedrock_runtime = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv(
                settings.PRIVATE_AWS_REGION, "us-west-1"
            ),  # Provide a default region
        )

        # Model IDs and parameters
        self.embed_model_id = os.getenv("EMBED_MODEL_ID", "amazon.titan-embed-text-v1")
        self.llm_model_id = os.getenv(
            "LLM_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"
        )
        self.max_tokens = int(os.getenv("MAX_TOKENS", "512"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.top_k = int(os.getenv("TOP_K", "5"))

    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generates embeddings for the given text.

        Args:
        text (str): The input text.

        Returns:
        List[float]: The generated embeddings.
        """
        body = json.dumps({"inputText": text})
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=self.embed_model_id,
                contentType="application/json",
                accept="application/json",
                body=body,
            )
        except ClientError as e:
            logging.error(f"Error invoking model: {e}")
            raise e

        response_body = json.loads(response["body"].read())
        return response_body["embedding"]

    async def get_context(self, query: str) -> List[str]:
        query_embedding = await self.generate_embeddings(query)
        logging.info(f"Generated query embedding of length: {len(query_embedding)}")
        results = await query_embeddings(query_embedding, top_k=self.top_k)
        logging.info(f"Query embedding results: {results}")

        context = []
        for match in results.get("matches", []):
            metadata = match.get("metadata", {})
            text = metadata.get("text")
            if text:
                context.append(text)
            else:
                logging.warning(
                    f"Warning: 'text' not found in metadata for match: {match}"
                )

        logging.info(f"Final context: {context}")
        return context

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(ClientError),
    )
    async def generate_response(self, query: str, context: List[str]) -> str:
        """
        Generates a response based on the given query and context.

        Args:
        query (str): The input query.
        context (List[str]): The relevant context.

        Returns:
        str: The generated response.
        """
        PROMPT_TEMPLATE = """
        You are a helpful AI assistant. Here is the context:
        {context}

        Human: {question}

        Assistant: Let me provide an answer based on the given context.
        """

        try:
            # Prepare the context
            context_text = "\n\n---\n\n".join(context)

            # Create the prompt
            prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            prompt = prompt_template.format(context=context_text, question=query)

            # Initialize the ChatBedrock model with explicit configuration
            model = ChatBedrock(
                model_id=self.llm_model_id,
                client=self.bedrock_runtime,
                model_kwargs={
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                },
            )

            # Generate the response
            response = model.invoke(prompt)

            return response.content

        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate response")

    async def chat(self, query: str) -> str:
        logging.info(f"Received query: {query}")
        context = await self.get_context(query)
        logging.info(f"Retrieved context: {context}")
        response = await self.generate_response(query, context)
        logging.info(f"Generated response: {response}")
        return response
