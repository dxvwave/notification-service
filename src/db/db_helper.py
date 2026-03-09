from shared.db.session import AsyncSessionManager

from core.config import settings

db_session_manager = AsyncSessionManager(database_url=settings.database_url)
