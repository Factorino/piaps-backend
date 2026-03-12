from pathlib import Path

from piaps.main.config.base import config


@config
class RendererConfig:
    templates_dir: str = "templates"

    @property
    def templates_path(self) -> Path:
        path = Path(self.templates_dir)
        if not path.exists():
            raise FileNotFoundError(f"Templates directory not found: {path}")
        return path
