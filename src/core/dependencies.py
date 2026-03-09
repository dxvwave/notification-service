from shared.dependencies import make_auth_dependencies

from interfaces.grpc.auth_client import AuthClient, auth_client_instance
from services.notification_service import NotificationService, notification_service


def get_auth_client() -> AuthClient:
    return auth_client_instance


def get_notification_service() -> NotificationService:
    return notification_service


get_current_user, get_current_active_user = make_auth_dependencies(get_auth_client)
