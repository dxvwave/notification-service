import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="Notification Service",
    description="Notification Management Service for Microservices",
    version="0.1.0",
    root_path="/api/v1/notifications",
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "notification-service",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
