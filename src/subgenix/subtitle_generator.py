from typing import List, Tuple, Sequence
from loguru import logger
import aiofiles
from .progress_manager import ProgressManager
import os

class SubtitleGenerator:
    MAX_SEGMENT_DURATION = 5.0  # Maximum duration for a single subtitle
    MAX_PAUSE_DURATION = 2.0  # Maximum duration of a pause before creating a new subtitle
    END_SENTENCE_PUNCTUATION = '.!?'  # Punctuation that typically ends a sentence

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
        """Group words into subtitle segments based on timing constraints and sentence structure."""
        segments = []
        current_segment = []
        current_start_time = word_timestamps[0][0]
        last_end_time = word_timestamps[0][1]

        for i, (start, end, word) in enumerate(word_timestamps):
            current_segment.append(word)
            segment_duration = end - current_start_time
            pause_duration = start - last_end_time

            # Check if we need to start a new segment
            if segment_duration >= self.MAX_SEGMENT_DURATION or pause_duration >= self.MAX_PAUSE_DURATION:
                # Try to find a better split point
                split_index = self._find_split_index(current_segment)
                if split_index > 0:
                    # Split the segment
                    first_part = current_segment[:split_index]
                    second_part = current_segment[split_index:]
                    
                    # Add the first part as a segment
                    segments.append((current_start_time, word_timestamps[i-len(second_part)][1], " ".join(first_part)))
                    
                    # Start a new segment with the second part
                    current_segment = second_part
                    current_start_time = word_timestamps[i-len(second_part)+1][0]
                else:
                    # If no good split point, just add the current segment
                    segments.append((current_start_time, end, " ".join(current_segment)))
                    current_segment = []
                    current_start_time = end

            last_end_time = end

        # Add the last segment
        if current_segment:
            segments.append((current_start_time, word_timestamps[-1][1], " ".join(current_segment)))

        return segments

    def _find_split_index(self, words: List[str]) -> int:
        """Find the best index to split a list of words, preferring sentence boundaries."""
        # First, try to find the last sentence-ending punctuation
        for i in range(len(words) - 1, -1, -1):
            if words[i][-1] in self.END_SENTENCE_PUNCTUATION:
                return i + 1  # Split after the punctuation
        
        # If no sentence boundary found, try to split at a natural pause (e.g., comma)
        for i in range(len(words) - 1, -1, -1):
            if words[i].endswith(','):
                return i + 1  # Split after the comma
        
        # If no good split point found, split in the middle
        return len(words) // 2

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
