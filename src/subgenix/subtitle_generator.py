from typing import List, Tuple, Sequence
from loguru import logger
import aiofiles
from .progress_manager import ProgressManager
import os

class SubtitleGenerator:
    MAX_SEGMENT_DURATION = 5.0  # Maximum duration for a single subtitle
    MAX_PAUSE_DURATION = 2.0  # Maximum duration of a pause before creating a new subtitle

    def __init__(self, progress_manager: ProgressManager):
        self.progress_manager = progress_manager
        logger.info("SubtitleGenerator initialized")

    async def generate_subtitles(self, word_timestamps: Sequence[Tuple[float, float, str]], output_file: str) -> str:
        """
        Generate subtitles from word timestamps and write them to an SRT file.

        Args:
            word_timestamps: A sequence of tuples containing (start_time, end_time, word).
            output_file: The path to the output file (can be with or without extension).

        Returns:
            The path to the generated SRT file.

        Raises:
            Exception: If there's an error during subtitle generation.
        """
        self.progress_manager.start_task("Generating subtitles")
        logger.info(f"Generating subtitles for output file: {output_file}")
        try:
            subtitle_segments = self._group_words_into_segments(word_timestamps)
            srt_filename = self._get_srt_filename(output_file)
            await self._write_srt_file(subtitle_segments, srt_filename)
            self.progress_manager.complete_task("Subtitles generated")
            return srt_filename
        except Exception as e:
            logger.exception(f"Error generating subtitles: {str(e)}")
            self.progress_manager.fail_task("Subtitle generation failed")
            raise

    def _get_srt_filename(self, output_file: str) -> str:
        """
        Convert the output filename to an SRT filename.
        
        This method ensures that the returned filename always has a .srt extension,
        regardless of whether the input filename had an extension or not.
        """
        # Split the path and filename
        directory, filename = os.path.split(output_file)
        
        # Remove any existing extension and add .srt
        base_name = os.path.splitext(filename)[0]
        srt_filename = f"{base_name}.srt"
        
        # Join the directory back with the new filename
        return os.path.join(directory, srt_filename)

    def _group_words_into_segments(self, word_timestamps: Sequence[Tuple[float, float, str]]) -> List[Tuple[float, float, str]]:
        """Group words into subtitle segments based on timing constraints."""
        segments = []
        current_segment = []
        current_start_time = word_timestamps[0][0]

        for i, (start, end, word) in enumerate(word_timestamps[1:], 1):
            current_segment.append(word)
            segment_duration = end - current_start_time
            pause_duration = start - word_timestamps[i-1][1]

            if segment_duration >= self.MAX_SEGMENT_DURATION or pause_duration >= self.MAX_PAUSE_DURATION:
                segments.append((current_start_time, word_timestamps[i-1][1], " ".join(current_segment)))
                current_segment = []
                current_start_time = start

        # Add the last segment
        if current_segment:
            segments.append((current_start_time, word_timestamps[-1][1], " ".join(current_segment)))

        return segments

    async def _write_srt_file(self, segments: Sequence[Tuple[float, float, str]], output_file: str):
        """Write the subtitle segments to an SRT file."""
        total_segments = len(segments)
        self.progress_manager.start_task(f"Writing {total_segments} subtitle segments", total=total_segments)
        try:
            async with aiofiles.open(output_file, "w") as f:
                for i, (start_time, end_time, text) in enumerate(segments, 1):
                    await f.write(f"{i}\n")
                    await f.write(f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n")
                    await f.write(f"{text}\n\n")
                    self.progress_manager.update_progress(1)
        except IOError as e:
            logger.error(f"Error writing SRT file: {str(e)}")
            raise
        finally:
            self.progress_manager.complete_task("Subtitle file written")

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format time in seconds to SRT time format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")
