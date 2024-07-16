from typing import List, Tuple
from loguru import logger
import aiofiles
from .progress_manager import ProgressManager
import os

class SubtitleGenerator:
    def __init__(self, progress_manager: ProgressManager):
        self.progress_manager = progress_manager
        logger.info("SubtitleGenerator initialized")

    async def generate_subtitles(self, word_timestamps: List[Tuple[float, float, str]], output_file: str) -> str:
        self.progress_manager.start_task("Generating subtitles")
        logger.info(f"Generating subtitles for output file: {output_file}")
        try:
            subtitle_segments = self._group_words_into_segments(word_timestamps)
            output_file = self._get_srt_filename(output_file)
            await self._write_srt_file(subtitle_segments, output_file)
            self.progress_manager.complete_task("Subtitles generated")
            return output_file
        except Exception as e:
            logger.error(f"Error generating subtitles: {str(e)}")
            self.progress_manager.fail_task("Subtitle generation failed")
            raise

    def _get_srt_filename(self, output_file: str) -> str:
        base_name = os.path.splitext(output_file)[0]
        return f"{base_name}.srt"

    def _group_words_into_segments(self, word_timestamps: List[Tuple[float, float, str]]) -> List[Tuple[float, float, str]]:
        segments = []
        current_segment = []
        current_start_time = word_timestamps[0][0]
        max_segment_duration = 5.0  # Maximum duration for a single subtitle
        max_pause_duration = 2.0  # Maximum duration of a pause before creating a new subtitle

        for i in range(1, len(word_timestamps)):
            start, end, word = word_timestamps[i]
            current_segment.append(word)
            if end - current_start_time >= max_segment_duration or end - word_timestamps[i - 1][1] >= max_pause_duration:
                segments.append((current_start_time, word_timestamps[i-1][1], " ".join(current_segment)))
                current_segment = []
                current_start_time = end

        # Add the last segment
        if current_segment:
            segments.append((current_start_time, word_timestamps[-1][1], " ".join(current_segment)))

        return segments

    async def _write_srt_file(self, segments: List[Tuple[float, float, str]], output_file: str):
        total_segments = len(segments)
        self.progress_manager.start_task(f"Writing {total_segments} subtitle segments", total=total_segments)
        async with aiofiles.open(output_file, "w") as f:
            for i, (start_time, end_time, text) in enumerate(segments, 1):
                await f.write(f"{i}\n")
                await f.write(f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n")
                await f.write(f"{text}\n\n")
                self.progress_manager.update_progress(1)
        self.progress_manager.complete_task("Subtitle file written")

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")
