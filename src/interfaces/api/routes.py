import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_active_user, get_notification_service
from db import db_session_manager
from services.notification_service import NotificationService
from .schemas import SubscriptionRead

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Subscriptions"])


@router.post(
    "/products/{product_id}/subscribe",
    response_model=SubscriptionRead,
    status_code=status.HTTP_201_CREATED,
)
async def subscribe_to_product(
    product_id: int,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    session: AsyncSession = Depends(db_session_manager.get_async_session),
    notification_service: NotificationService = Depends(get_notification_service),
):
    subscription = await notification_service.subscribe(
        session,
        user_id=current_user["id"],
        product_id=product_id,
    )
    return subscription


@router.delete(
    "/products/{product_id}/subscribe",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unsubscribe_from_product(
    product_id: int,
    current_user: Annotated[dict, Depends(get_current_active_user)],
    session: AsyncSession = Depends(db_session_manager.get_async_session),
    notification_service: NotificationService = Depends(get_notification_service),
):
    await notification_service.unsubscribe(
        session,
        user_id=current_user["id"],
        product_id=product_id,
    )


@router.get(
    "/subscriptions",
    response_model=list[SubscriptionRead],
)
async def get_my_subscriptions(
    current_user: Annotated[dict, Depends(get_current_active_user)],
    session: AsyncSession = Depends(db_session_manager.get_async_session),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.get_subscriptions(session, user_id=current_user["id"])

