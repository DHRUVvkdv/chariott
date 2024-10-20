# services/agent_manager.py

from .rag_interaction_service import RAGInteractionService
from .booking_service import BookingService
from .hotel_service import HotelService
from .document_processor import DocumentProcessorService
from .dynamodb_service import DynamoDBService
from .embedding_service import EmbeddingService
from .pinecone_service import PineconeService
from .rag_service import RAGService
from .request_service import RequestService
from .s3_service import S3Service
from .user_service import UserService
from .top_user_recommendation_service import TopUserRecommendationsService


class AgentManager:
    def __init__(self):
        self.rag_interaction_service = RAGInteractionService()
        self.booking_service = BookingService()
        self.hotel_service = HotelService()
        self.document_processor_service = DocumentProcessorService()
        self.dynamodb_service = DynamoDBService()
        self.embedding_service = EmbeddingService()
        self.pinecone_service = PineconeService()
        self.rag_service = RAGService()
        self.request_service = RequestService()
        self.s3_service = S3Service()
        self.user_service = UserService()
        self.top_user_recommendations_service = TopUserRecommendationsService()

    def process_request(self, request_type, request_data):
        if request_type == "rag_interaction":
            return self.rag_interaction_service.process(request_data)
        elif request_type == "booking":
            return self.booking_service.process(request_data)
        elif request_type == "hotel_info":
            return self.hotel_service.process(request_data)
        elif request_type == "process_document":
            return self.document_processor_service.process(request_data)
        elif request_type == "dynamodb_operation":
            return self.dynamodb_service.process(request_data)
        elif request_type == "generate_embedding":
            return self.embedding_service.generate_embedding(request_data)
        elif request_type == "pinecone_operation":
            return self.pinecone_service.process(request_data)
        elif request_type == "rag_query":
            return self.rag_service.query(request_data)
        elif request_type == "handle_request":
            return self.request_service.handle(request_data)
        elif request_type == "s3_operation":
            return self.s3_service.process(request_data)
        elif request_type == "user_operation":
            return self.user_service.process(request_data)
        elif request_type == "top_user_recommendations":
            return self.top_user_recommendations_service.get_recommendations(
                request_data
            )
        elif request_type == "analyze_user_interactions":
            return self.top_user_recommendations_service.analyze_user_interactions(
                request_data
            )
        else:
            raise ValueError(f"Unknown request type: {request_type}")

    def get_rag_interaction_service(self):
        return self.rag_interaction_service

    def get_booking_service(self):
        return self.booking_service

    def get_hotel_service(self):
        return self.hotel_service

    def get_document_processor_service(self):
        return self.document_processor_service

    def get_dynamodb_service(self):
        return self.dynamodb_service

    def get_embedding_service(self):
        return self.embedding_service

    def get_pinecone_service(self):
        return self.pinecone_service

    def get_rag_service(self):
        return self.rag_service

    def get_request_service(self):
        return self.request_service

    def get_s3_service(self):
        return self.s3_service

    def get_user_service(self):
        return self.user_service

    def get_top_user_recommendations_service(self):
        return self.top_user_recommendations_service
