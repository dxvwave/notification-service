import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.subscription import Subscription
from core.exceptions import SubscriptionAlreadyExistsError, SubscriptionNotFoundError

logger = logging.getLogger(__name__)


class NotificationService:
    async def subscribe(
        self,
        session: AsyncSession,
        user_id: int,
        product_id: int,
    ) -> Subscription:
        existing = await session.scalar(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.product_id == product_id,
            )
        )
        if existing:
            raise SubscriptionAlreadyExistsError(
                f"User {user_id} is already subscribed to product {product_id}"
            )

        subscription = Subscription(user_id=user_id, product_id=product_id)
        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)

        logger.info(f"User {user_id} subscribed to product {product_id}")
        return subscription

    async def unsubscribe(
        self,
        session: AsyncSession,
        user_id: int,
        product_id: int,
    ) -> None:
        result = await session.execute(
            delete(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.product_id == product_id,
            )
        )
        if result.rowcount == 0:
            raise SubscriptionNotFoundError(
                f"Subscription for user {user_id} on product {product_id} not found"
            )

        await session.commit()
        logger.info(f"User {user_id} unsubscribed from product {product_id}")

    async def get_subscriptions(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[Subscription]:
        result = await session.scalars(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        return list(result.all())

    async def get_subscribers_for_product(
        self,
        session: AsyncSession,
        product_id: int,
    ) -> list[Subscription]:
        result = await session.scalars(
            select(Subscription).where(Subscription.product_id == product_id)
        )
        return list(result.all())

    async def handle_price_changed(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> None:
        product_id = payload["id"]
        previous_price = payload["previous_price"]
        new_price = payload["new_price"]

        subscribers = await self.get_subscribers_for_product(session, product_id)

        if not subscribers:
            logger.info(f"No subscribers for product {product_id}, skipping notification")
            return

        logger.info(
            f"Notifying {len(subscribers)} subscriber(s) about price change "
            f"on product {product_id}: {previous_price} -> {new_price}"
        )
        for sub in subscribers:
            # Delivery mechanism (email, push, etc.) goes here.
            logger.info(
                f"[NOTIFY] user_id={sub.user_id} | product_id={product_id} | "
                f"{previous_price} -> {new_price}"
            )


notification_service = NotificationService()
