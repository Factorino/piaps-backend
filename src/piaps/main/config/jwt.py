from functools import cached_property
from pathlib import Path

from piaps.main.config.base import config


@config
class JWTConfig:
    algorithm: str = "RS256"
    private_key_path: str = "certs/private.pem"
    public_key_path: str = "certs/public.pem"
    access_ttl_minutes: int = 15
    refresh_ttl_minutes: int = 7 * 24 * 60  # 7 days

    @cached_property
    def private_key(self) -> str:
        path = Path(self.private_key_path)
        if not path.exists():
            raise FileNotFoundError(f"Private key not found at {path}")
        return path.read_text(encoding="utf-8")

    @cached_property
    def public_key(self) -> str:
        path = Path(self.public_key_path)
        if not path.exists():
            raise FileNotFoundError(f"Public key not found at {path}")
        return path.read_text(encoding="utf-8")
