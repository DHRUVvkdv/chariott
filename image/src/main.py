from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from middleware.auth import AuthMiddleware
from fastapi.openapi.utils import get_openapi
from mangum import Mangum
import logging
from api.endpoints import document

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(title=settings.PROJECT_NAME)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Teaching Asssistant",
        version="1.0.0",
        description="API for the Teaching Assistant application",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "API-Key"}
    }
    openapi_schema["security"] = [{"ApiKeyAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


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
    return Response(status_code=302, headers={"Location": "/docs"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
