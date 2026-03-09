from fastapi import status

from shared.exceptions import ApplicationException, AuthenticationError, UnauthorizedError, InactiveUserError  # noqa: F401


class SubscriptionNotFoundError(ApplicationException):
    pass


class SubscriptionAlreadyExistsError(ApplicationException):
    pass


EXCEPTION_MAPPING = {
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    InactiveUserError: status.HTTP_403_FORBIDDEN,
    SubscriptionNotFoundError: status.HTTP_404_NOT_FOUND,
    SubscriptionAlreadyExistsError: status.HTTP_409_CONFLICT,
}
