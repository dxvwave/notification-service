import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from services.rabbitmq_client import rabbit_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for the FastAPI application."""
    # Connect to RabbitMQ
    await rabbit_client.connect()
    await rabbit_client.setup_topology("product_events", "notification_queue", ["product.created"])
    
    # Run the consumer in the background
    consumer_task = asyncio.create_task(rabbit_client.consume())

    yield

    # Shutdown
    consumer_task.cancel()
    await rabbit_client.close()


app = FastAPI(
    title="Notification Service",
    description="Notification Management Service for Microservices",
    version="0.1.0",
    root_path="/api/v1/notifications",
    lifespan=lifespan,
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
