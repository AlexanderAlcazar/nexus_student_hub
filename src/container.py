from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from database.database_manager import Database
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.profile_service import ProfileService


@dataclass(frozen=True)
class AppSettings:
    database_name: str = "nexus_student_hub"
    data_dir: Optional[str] = None
    schema_path: Optional[str] = None
    database_dsn: Optional[str] = None
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "postgres"
    database_password: str = "postgres"
    jwt_secret: str = "dev-only-change-me-at-least-32-bytes-long"
    jwt_access_ttl_seconds: int = 900
    jwt_refresh_ttl_seconds: int = 2592000


class ApplicationContainer:
    def __init__(self, settings: AppSettings = AppSettings()):
        self.settings = settings

    @cached_property
    def database(self) -> Database:
        return Database(
            db_name=self.settings.database_name,
            data_dir=self.settings.data_dir,
            schema_path=self.settings.schema_path,
            dsn=self.settings.database_dsn,
            host=self.settings.database_host,
            port=self.settings.database_port,
            user=self.settings.database_user,
            password=self.settings.database_password,
        )

    @cached_property
    def user_repository(self) -> UserRepository:
        return UserRepository(self.database)

    @cached_property
    def auth_service(self) -> AuthService:
        return AuthService(
            self.user_repository,
            jwt_secret=self.settings.jwt_secret,
            access_ttl_seconds=self.settings.jwt_access_ttl_seconds,
            refresh_ttl_seconds=self.settings.jwt_refresh_ttl_seconds,
        )

    @cached_property
    def profile_service(self) -> ProfileService:
        return ProfileService(self.user_repository)


def build_container(settings: Optional[AppSettings] = None) -> ApplicationContainer:
    return ApplicationContainer(settings or AppSettings())
