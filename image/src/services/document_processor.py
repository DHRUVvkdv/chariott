from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from services.s3_service import get_file_from_s3
from services.embedding_service import generate_embeddings
from services.pinecone_service import store_embeddings
from services.dynamodb_service import update_document_status
import tempfile


async def process_document(document_id: str, s3_url: str, user_id: str):
    # 1. Retrieve document from S3
    file_content = await get_file_from_s3(s3_url)

    # 2. Save the content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_content.getvalue())
        temp_file_path = temp_file.name

    # 3. Use PyPDFLoader to load and parse the PDF
    loader = PyPDFLoader(temp_file_path)
    pages = loader.load_and_split()

    # 4. Extract text content from pages
    text_content = "\n".join([page.page_content for page in pages])

    # 5. Chunk document
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text_content)

    # 6. Generate embeddings
    embeddings = await generate_embeddings(chunks)

    # 7. Store embeddings in Pinecone
    await store_embeddings(
        document_id,
        embeddings,
        metadata={"s3_url": s3_url, "document_id": document_id, "user_id": user_id},
    )

    # 8. Update document status in DynamoDB
    await update_document_status(document_id, "completed", s3_url, user_id)
