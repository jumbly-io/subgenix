import json
from pathlib import Path
from typing import Any, Optional, Set
from loguru import logger
import asyncio


class CacheManager:
    def __init__(self, video_file: str):
        self.video_file = Path(video_file)
        self.base_dir = self.video_file.parent / f"{self.video_file.stem}_cache"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_dir / "metadata.json"
        self.metadata = self._load_metadata()
        self.temp_files: Set[Path] = set()

        logger.info(f"CacheManager initialized for video file: {self.video_file}")

    def _load_metadata(self) -> dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f)

    def get_cache_path(self, filename: str) -> Path:
        path = self.base_dir / filename
        self.temp_files.add(path)
        return path

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

    async def cleanup(self):
        logger.info("Starting cleanup of temporary files")
        for file in self.temp_files:
            try:
                if await asyncio.to_thread(file.exists):
                    await asyncio.to_thread(file.unlink)
                    logger.debug(f"Removed temporary file: {file}")
            except Exception as e:
                logger.error(f"Error removing temporary file {file}: {str(e)}")

        if not any(self.base_dir.iterdir()):
            await asyncio.to_thread(self.base_dir.rmdir)
            logger.info(f"Removed empty cache directory: {self.base_dir}")
        else:
            logger.info(f"Cache directory not empty, keeping: {self.base_dir}")

        self.temp_files.clear()
        logger.info("Cleanup completed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._save_metadata()
