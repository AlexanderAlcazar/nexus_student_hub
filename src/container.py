from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from database.database_manager import Database
from repositories.user_repository import UserRepository
from services.auth_service import AuthService


@dataclass(frozen=True)
class AppSettings:
    database_name: str = "nexus.db"
    data_dir: Optional[str] = None
    schema_path: Optional[str] = None


class ApplicationContainer:
    def __init__(self, settings: AppSettings = AppSettings()):
        self.settings = settings

    @cached_property
    def database(self) -> Database:
        return Database(
            db_name=self.settings.database_name,
            data_dir=self.settings.data_dir,
            schema_path=self.settings.schema_path,
        )

    @cached_property
    def user_repository(self) -> UserRepository:
        return UserRepository(self.database)

    @cached_property
    def auth_service(self) -> AuthService:
        return AuthService(self.user_repository)


def build_container(settings: Optional[AppSettings] = None) -> ApplicationContainer:
    return ApplicationContainer(settings or AppSettings())
