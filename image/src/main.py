from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

# from api.endpoints import user
# from db.mongodb import connect_to_mongo, close_mongo_connection
from middleware.auth import AuthMiddleware
from mangum import Mangum
import logging

# from api.endpoints import user, building, review, profile, plan, aggregation

logging.basicConfig(level=logging.DEBUG)


app = FastAPI(title=settings.PROJECT_NAME)

# # Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom authentication middleware
app.add_middleware(AuthMiddleware)

# app.add_event_handler("startup", connect_to_mongo)
# app.add_event_handler("shutdown", close_mongo_connection)

# app.include_router(user.router, prefix="/api/users", tags=["users"])
# app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
# app.include_router(building.router, prefix="/api/buildings", tags=["buildings"])
# app.include_router(review.router, prefix="/api/review", tags=["review"])
# app.include_router(plan.router, prefix="/api/plan", tags=["plan"])
# app.include_router(
#     aggregation.router, prefix="/api/aggregations", tags=["aggregations"]
# )


handler = Mangum(app)


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


@app.get("/test")
async def read_root():
    return {"message": "Mike does it work?"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
