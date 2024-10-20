from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.endpoints import user, document, request
from middleware.auth import AuthMiddleware
from fastapi.openapi.utils import get_openapi
from mangum import Mangum
import logging
from api.endpoints import booking
from api.endpoints import hotel, rag_interaction
from api.endpoints import vector
from services.agent_manager import AgentManager
from api.endpoints import top_user_recommendations


logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.PROJECT_NAME)

agent_manager = AgentManager()


def get_agent_manager():
    return agent_manager


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Chariott API",
        version="1.0.0",
        description="API for the Chariott Hospitality and Travel application",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "API-Key"}
    }
    openapi_schema["security"] = [{"ApiKeyAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(AuthMiddleware)

app.include_router(user.router, prefix="/api/auth", tags=["auth"])
app.include_router(document.router, prefix="/api/documents", tags=["documents"])
app.include_router(request.router, prefix="/api/requests", tags=["requests"])
app.include_router(booking.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(hotel.router, prefix="/api/hotels", tags=["hotels"])
app.include_router(rag_interaction.router, prefix="/api/rag", tags=["rag"])
app.include_router(vector.router, prefix="/api/vector", tags=["vectors"])
app.include_router(
    top_user_recommendations.router,
    prefix="/api/top_user_recommendations",
    tags=["top_user_recommendations"],
)


handler = Mangum(app)


@app.get("/")
async def read_root():
    return Response(status_code=302, headers={"Location": "/docs"})


@app.get("/test")
async def read_root():
    return {"message": "DHRUV Rocks!!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
