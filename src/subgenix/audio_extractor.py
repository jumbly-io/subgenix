import asyncio
from pathlib import Path
from loguru import logger
from moviepy.editor import VideoFileClip  # type: ignore
from .cache_manager import CacheManager
from .progress_manager import ProgressManager


class AudioExtractor:
    def __init__(self, cache_manager: CacheManager, progress_manager: ProgressManager):
        self.cache_manager = cache_manager
        self.progress_manager = progress_manager

    async def extract_audio(self, video_file: str) -> str:
        video_path = Path(video_file)
        audio_file = self.cache_manager.get_cache_path(video_path.stem + ".wav")

        if audio_file.exists():
            logger.info(f"Using cached audio file: {audio_file}")
            return str(audio_file)

        logger.info(f"Extracting audio from {video_file}")
        self.progress_manager.start_task("Extracting audio")

        try:
            with VideoFileClip(video_file) as video:
                audio = video.audio
                if audio is None:
                    raise ValueError(f"No audio track found in {video_file}")

                # Use asyncio to run the CPU-bound task in a separate thread
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, lambda: audio.write_audiofile(str(audio_file), codec="pcm_s16le", progress_bar=False)
                )

            logger.info(f"Audio extracted successfully: {audio_file}")
            self.progress_manager.complete_task("Extracting audio")
            return str(audio_file)

        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            self.progress_manager.fail_task("Extracting audio")
            raise

    async def get_video_duration(self, video_file: str) -> float:
        try:
            with VideoFileClip(video_file) as video:
                return float(video.duration)
        except Exception as e:
            logger.error(f"Error getting video duration: {str(e)}")
            raise

    async def process_video(self, video_file: str) -> tuple[str, float]:
        audio_file = await self.extract_audio(video_file)
        duration = await self.get_video_duration(video_file)
        return audio_file, duration
