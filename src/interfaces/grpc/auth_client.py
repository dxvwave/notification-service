from shared.grpc.auth_client import AuthClient

from core.config import settings


auth_client_instance = AuthClient(
    host=settings.auth_grpc_client_host,
    port=settings.auth_grpc_client_port,
)

__all__ = ["AuthClient", "auth_client_instance"]
