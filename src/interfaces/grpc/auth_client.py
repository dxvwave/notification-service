import logging
import grpc
from contracts.gen import auth_pb2, auth_pb2_grpc
from core.config import settings

logger = logging.getLogger(__name__)


class AuthClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None

    async def connect(self):
        if self.channel is None:
            self.channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
            self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)
            logger.info(f"Auth client connected to {self.host}:{self.port}")

    async def close(self):
        if self.channel:
            await self.channel.close()
            logger.info("Auth client connection closed")

    async def validate_token(self, token: str) -> auth_pb2.ValidateResponse:
        """
        Validate a JWT token via gRPC.

        Args:
            token: JWT token to validate

        Returns:
            ValidateResponse object with is_valid and user fields
        """
        try:
            request = auth_pb2.ValidateRequest(token=token)
            response = await self.stub.ValidateToken(request)
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error during token validation: {e.code()} - {e.details()}"
            )
            return auth_pb2.ValidateResponse(is_valid=False)


auth_client_instance = AuthClient(
    host=settings.auth_grpc_client_host,
    port=settings.auth_grpc_client_port,
)
