from fastapi import status


class ApplicationException(Exception):
    """Base exception for the application."""

    def __init__(self, message: str):
        self.message = message


class AuthenticationError(ApplicationException):
    """Raised when authentication fails."""

    pass


class UnauthorizedError(AuthenticationError):
    """Raised when a user is not authorized to perform an action."""

    pass


class InactiveUserError(AuthenticationError):
    """Raised when an inactive user attempts to perform an action."""

    pass


class SubscriptionNotFoundError(ApplicationException):
    """Raised when a subscription does not exist."""

    pass


class SubscriptionAlreadyExistsError(ApplicationException):
    """Raised when a subscription already exists."""

    pass


EXCEPTION_MAPPING = {
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    InactiveUserError: status.HTTP_403_FORBIDDEN,
    SubscriptionNotFoundError: status.HTTP_404_NOT_FOUND,
    SubscriptionAlreadyExistsError: status.HTTP_409_CONFLICT,
}
