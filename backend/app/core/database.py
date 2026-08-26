import asyncio

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


class MongoManager:
    """MongoDB connection manager with an in-memory demo fallback.

    If a real MongoDB server is unreachable at startup, the manager falls
    back to an in-memory Mongo-compatible client (mongomock-motor) so the
    full agent workflow stays runnable anywhere. Data in this mode is
    NON-PERSISTENT and must be presented as DEMO MODE in the UI.
    """

    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None
        self.db_mode: str = "uninitialized"

    def connect(self) -> AsyncIOMotorDatabase:
        if self._client is None:
            settings = get_settings()
            try:
                client = AsyncIOMotorClient(
                    settings.mongo_uri,
                    serverSelectionTimeoutMS=1500,
                    connectTimeoutMS=1500,
                )
                # Force a round-trip so we know immediately whether Mongo is up.
                asyncio.get_event_loop().run_until_complete(
                    client.admin.command("ping")
                )
                self._client = client
                self.db_mode = "mongodb"
            except Exception:
                from mongomock_motor import AsyncMongoMockClient

                self._client = AsyncMongoMockClient()
                self.db_mode = "memory-demo"
        return self._client[get_settings().mongo_db]

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self.db_mode = "uninitialized"


mongo_manager = MongoManager()


def get_db() -> AsyncIOMotorDatabase:
    return mongo_manager.connect()
