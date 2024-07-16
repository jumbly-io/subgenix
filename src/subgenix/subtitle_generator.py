from typing import List, Tuple
from loguru import logger
import aiofiles
from .progress_manager import ProgressManager


class SubtitleGenerator:
    def __init__(self, progress_manager: ProgressManager):
        self.progress_manager = progress_manager
        logger.info("SubtitleGenerator initialized")

    async def generate_subtitles(self, word_timestamps: List[Tuple[float, float, str]], output_file: str) -> str:
        self.progress_manager.start_task("Generating subtitles")
        logger.info(f"Generating subtitles for output file: {output_file}")
        try:
            subtitle_segments = self._group_words_into_segments(word_timestamps)
            await self._write_srt_file(subtitle_segments, output_file)
            self.progress_manager.complete_task("Subtitles generated")
            return output_file
        except Exception as e:
            logger.error(f"Error generating subtitles: {str(e)}")
            self.progress_manager.fail_task("Subtitle generation failed")
            raise


    def _group_words_into_segments(self, word_timestamps):
        segments = []
        current_segment = []
        current_start_time = word_timestamps[0][0]

        for start, end, word in word_timestamps:
            current_segment.append(word)
            if word.endswith('.') or word.endswith('?') or word.endswith('!'):
                segment_text = ' '.join(current_segment)
                segments.append((current_start_time, end, segment_text))
                current_segment = []
                current_start_time = end

    # Add any remaining words as the final segment
        if current_segment:
            segment_text = ' '.join(current_segment)
            segments.append((current_start_time, word_timestamps[-1][1], segment_text))
            min_gap_duration = 0.5      # Define the minimum gap duration
            max_segment_duration = 5.0  # Maximum duration for a single subtitle
        for i in range(len(segments) - 1):
            start_time, end_time, text = segments[i]
            next_start_time, _, _ = segments[i + 1]

            if next_start_time - end_time < min_gap_duration:
                new_end_time = min(end_time + max_segment_duration, next_start_time)
                segments[i] = (start_time, new_end_time, text)

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
