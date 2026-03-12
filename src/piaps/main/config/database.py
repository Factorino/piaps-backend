from piaps.main.config.base import config


@config
class _SqliteDatabaseConfig:
    db_path: str = "data/app_db.sqlite"
    driver: str = "sqlite+aiosqlite"

    @property
    def dsn(self) -> str:
        return f"{self.driver}:///{self.db_path}"


@config
class _PostgresDatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"  # noqa: S105
    db_name: str = "app_db"
    driver: str = "postgresql+psycopg3"

    @property
    def dsn(self) -> str:
        return (
            f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        )


@config
class DatabaseConfig(_SqliteDatabaseConfig):
    pass
