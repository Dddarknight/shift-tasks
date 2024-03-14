from src.adapters.database import AsyncSessionManager


class BaseService:
    def __init__(
        self,
        session_factory: AsyncSessionManager,
    ) -> None:
        self.session_factory = session_factory
