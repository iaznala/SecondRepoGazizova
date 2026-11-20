from typing import Any, List

from beanie import init_beanie
from pymongo import AsyncMongoClient
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from models.events import Event
from models.users import User


class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env")

    async def initialize_database(self):
        client = AsyncMongoClient(self.DATABASE_URL)
        await client.admin.command("ping")

        await init_beanie(
            database=client.get_default_database(),
            document_models=[Event, User]
        )


class Database:
    def __init__(self, model):
        self.model = model

    async def save(self, document) -> None:
        await document.create()

    async def get(self, id: str) -> Any:
        document = await self.model.get(id)
        return document if document else False

    async def get_all(self) -> List[Any]:
        return await self.model.find_all().to_list()

    async def update(self, id: str, body: BaseModel) -> Any:
        document = await self.get(id)

        if not document:
            return False

        update_data = body.model_dump(exclude_none=True)

        if update_data:
            await document.update({"$set": update_data})

        return await self.get(id)

    async def delete(self, id: str) -> bool:
        document = await self.get(id)

        if not document:
            return False

        await document.delete()
        return True