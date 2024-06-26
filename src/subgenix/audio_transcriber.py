import asyncio
from typing import Optional, List, Tuple, cast
from loguru import logger
import whisper  # type: ignore
import torch
from .progress_manager import ProgressManager


class AudioTranscriber:
    def __init__(self, progress_manager: ProgressManager, model_name: str = "base"):
        self.progress_manager = progress_manager
        self.model_name = model_name
        self.model = None
        logger.info("AudioTranscriber initialized")

    def load_model(self, use_gpu: bool):
        device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(self.model_name, device=device)
        return self.model

    async def transcribe_audio(
        self, audio_file: str, language: Optional[str], use_gpu: bool
    ) -> List[Tuple[float, float, str]]:
        self.progress_manager.start_task("Loading Whisper model")
        logger.info(f"Loading Whisper model: {self.model_name}")

        try:
            model = self.load_model(use_gpu)
            self.progress_manager.complete_task("Model loaded")

            self.progress_manager.start_task("Transcribing audio")
            logger.info(f"Transcribing audio file: {audio_file}")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: model.transcribe(audio_file, language=language, word_timestamps=True)
            )

            word_timestamps = self._extract_word_timestamps(result)
            self.progress_manager.complete_task("Transcription completed")
            logger.info(f"Transcription completed: {len(word_timestamps)} words")
            return word_timestamps

        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            self.progress_manager.fail_task("Transcription failed")
            raise

    def _extract_word_timestamps(self, result: dict) -> List[Tuple[float, float, str]]:
        word_timestamps = []
        for segment in result["segments"]:
            for word in segment["words"]:
                start = word["start"]
                end = word["end"]
                text = word["word"]
                word_timestamps.append((start, end, text))
        return word_timestamps

    async def detect_language(self, audio_file: str) -> str:
        model = self.load_model(use_gpu=False)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: model.detect_language(audio_file))
        return cast(str, result)
