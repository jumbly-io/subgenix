import os
import json
from pathlib import Path
from typing import Any, Optional
from loguru import logger


class CacheManager:
    def __init__(self, video_file: str):
        self.video_file = Path(video_file)
        self.base_dir = self.video_file.parent / f"{self.video_file.stem}_cache"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_dir / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f)

    def get_cache_path(self, filename: str) -> Path:
        return self.base_dir / filename

    def cache_exists(self, key: str) -> bool:
        return key in self.metadata and self.get_cache_path(self.metadata[key]["filename"]).exists()

    def get_cache(self, key: str) -> Optional[Path]:
        if self.cache_exists(key):
            return self.get_cache_path(self.metadata[key]["filename"])
        return None

    def set_cache(self, key: str, data: Any, filename: str):
        cache_path = self.get_cache_path(filename)

        if isinstance(data, (str, bytes)):
            mode = "wb" if isinstance(data, bytes) else "w"
            with open(cache_path, mode) as f:
                f.write(data)
        elif isinstance(data, dict):
            with open(cache_path, "w") as f:
                json.dump(data, f)
        else:
            raise ValueError(f"Unsupported data type for caching: {type(data)}")

        self.metadata[key] = {"filename": filename, "type": type(data).__name__}
        self._save_metadata()

    def clear_cache(self, key: Optional[str] = None):
        if key is None:
            # Clear all cache
            for file in self.base_dir.iterdir():
                if file.is_file():
                    file.unlink()
            self.metadata = {}
        elif key in self.metadata:
            # Clear specific cache
            cache_path = self.get_cache_path(self.metadata[key]["filename"])
            if cache_path.exists():
                cache_path.unlink()
            del self.metadata[key]

        self._save_metadata()

    def get_cache_size(self) -> int:
        return sum(f.stat().st_size for f in self.base_dir.glob("**/*") if f.is_file())

    def get_cache_info(self) -> dict:
        return {
            "cache_size": self.get_cache_size(),
            "num_files": len(list(self.base_dir.glob("**/*"))),
            "metadata": self.metadata,
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._save_metadata()


logger.info(f"CacheManager initialized for video file: {self.video_file}")
