"""Environment settings. Relative database paths always start at the repo root."""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    database_path: Path
    cors_allowed_origins: tuple[str, ...] = ("http://localhost:3000",)

    @classmethod
    def from_environment(cls):
        path = Path(os.getenv("DATABASE_PATH", "data/greater-melbourne-v1/yfn.sqlite"))
        if not path.is_absolute():
            path = ROOT / path
        try:
            origins = json.loads(os.getenv("CORS_ALLOWED_ORIGINS", '["http://localhost:3000"]'))
            if not isinstance(origins, list):
                raise ValueError
            for origin in origins:
                if not isinstance(origin, str):
                    raise ValueError
                url = urlsplit(origin)
                if (url.scheme not in {"http", "https"} or not url.hostname
                        or url.path or url.query or url.fragment or url.username
                        or url.password or "*" in origin):
                    raise ValueError
                _ = url.port  # Reject malformed port numbers.
        except (ValueError, TypeError) as exc:
            raise ValueError("CORS_ALLOWED_ORIGINS must be a JSON array of HTTP(S) origins without paths.") from exc
        return cls(path.resolve(), tuple(origins))
