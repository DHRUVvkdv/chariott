# services/top_user_recommendations_service.py

import boto3
from typing import List
import json
from .rag_interaction_service import RAGInteractionService
from ..utils.utils import preprocess_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation


class TopUserRecommendationsService:
    def __init__(self):
        self.rag_service = RAGInteractionService()
        self.bedrock_runtime = boto3.client("bedrock-runtime")
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        self.lda_model = LatentDirichletAllocation(n_components=5, random_state=42)

    def get_recommendations(self, user_query: str) -> str:
        # Step 1: Get RAG interaction results
        rag_results = self.rag_service.process(user_query)

        # Step 2: Perform ML semantic analysis
        preprocessed_results = [preprocess_text(result) for result in rag_results]
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(preprocessed_results)
        lda_output = self.lda_model.fit_transform(tfidf_matrix)

        # Extract top topics and their keywords
        topics = []
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_words = [feature_names[i] for i in topic.argsort()[: -10 - 1 : -1]]
            topics.append(f"Topic {topic_idx + 1}: {', '.join(top_words)}")

        # Step 3: Prepare input for Claude
        claude_input = f"""
        User Query: {user_query}

        RAG Results:
        {json.dumps(rag_results, indent=2)}

        Semantic Analysis Results:
        {json.dumps(topics, indent=2)}

        Based on the user query, RAG results, and semantic analysis, please provide top recommendations for the user. 
        Consider the most relevant information and insights from the analysis.
        """

        # Step 4: Call AWS Bedrock's Claude
        response = self.bedrock_runtime.invoke_model(
            modelId="anthropic.claude-v2",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "prompt": claude_input,
                    "max_tokens_to_sample": 500,
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            ),
        )

        # Step 5: Process and return Claude's response
        claude_response = json.loads(response["body"].read())
        recommendations = claude_response["completion"]

        return recommendations.strip()

    def analyze_user_interactions(self, user_interactions: List[str]) -> str:
        # Preprocess user interactions
        preprocessed_interactions = [
            preprocess_text(interaction) for interaction in user_interactions
        ]

        # Perform TF-IDF and LDA analysis
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(preprocessed_interactions)
        lda_output = self.lda_model.fit_transform(tfidf_matrix)

        # Extract top topics and their keywords
        topics = []
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_words = [feature_names[i] for i in topic.argsort()[: -10 - 1 : -1]]
            topics.append(f"Topic {topic_idx + 1}: {', '.join(top_words)}")

        # Prepare input for Claude
        claude_input = f"""
        User Interactions Analysis:
        {json.dumps(topics, indent=2)}

        Based on the analysis of user interactions, please provide insights and recommendations for improving user engagement and satisfaction.
        Consider the most prominent topics and patterns in user behavior.
        """

        # Call AWS Bedrock's Claude
        response = self.bedrock_runtime.invoke_model(
            modelId="anthropic.claude-v2",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "prompt": claude_input,
                    "max_tokens_to_sample": 500,
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            ),
        )

        # Process and return Claude's response
        claude_response = json.loads(response["body"].read())
        analysis_results = claude_response["completion"]

        return analysis_results.strip()
