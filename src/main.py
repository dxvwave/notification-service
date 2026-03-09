import asyncio
import logging

import uvicorn
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.concurrency import asynccontextmanager
from fastapi import FastAPI

from core.logging_config import setup_logging
from core.exceptions import EXCEPTION_MAPPING, ApplicationException

setup_logging()
from db import db_session_manager
from interfaces.grpc.auth_client import auth_client_instance
from interfaces.api.routes import router
from services.rabbitmq_client import rabbit_client
from services.notification_service import notification_service

logger = logging.getLogger(__name__)


async def on_message(routing_key: str, payload: dict) -> None:
    """Top-level RabbitMQ message dispatcher."""
    if routing_key == "product.price_changed":
        async with db_session_manager.sessionmaker() as session:
            await notification_service.handle_price_changed(session, payload)
    else:
        logger.warning(f"Unhandled routing key: {routing_key}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # gRPC auth client
    await auth_client_instance.connect()

    # RabbitMQ — subscribe to price change events
    await rabbit_client.connect()
    await rabbit_client.setup_topology(
        "product_events",
        "notification_queue",
        ["product.price_changed"],
    )
    rabbit_client.set_handler(on_message)
    consumer_task = asyncio.create_task(rabbit_client.consume())

    def _on_consumer_done(task: asyncio.Task) -> None:
        if not task.cancelled() and task.exception():
            logger.error("Consumer task died unexpectedly", exc_info=task.exception())

    consumer_task.add_done_callback(_on_consumer_done)

    yield

    consumer_task.cancel()
    await rabbit_client.close()
    await auth_client_instance.close()
    await db_session_manager.close()


app = FastAPI(
    title="Notification Service",
    description="Notification Management Service for Microservices",
    version="0.1.0",
    root_path="/api/v1/notifications",
    lifespan=lifespan,
)


@app.exception_handler(ApplicationException)
async def application_exception_handler(request: Request, exc: ApplicationException):
    http_status = EXCEPTION_MAPPING.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JSONResponse(status_code=http_status, content={"detail": exc.message})


app.include_router(router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "notification-service"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

