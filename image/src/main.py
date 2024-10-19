from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from middleware.auth import AuthMiddleware
from mangum import Mangum
import logging
from api.endpoints import document

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

app.include_router(document.router, prefix="/api/documents", tags=["documents"])

handler = Mangum(app)


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
