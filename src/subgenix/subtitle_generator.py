from typing import List, Tuple, Sequence
from loguru import logger
import aiofiles
from .progress_manager import ProgressManager
import os


class SubtitleGenerator:
    MAX_SEGMENT_DURATION = 5.0  # Maximum duration for a single subtitle
    MAX_PAUSE_DURATION = 2.0  # Maximum duration of a pause before creating a new sub
    END_SENTENCE_PUNCTUATION = ".!?"

    def __init__(self, progress_manager: ProgressManager):
        self.progress_manager = progress_manager
        logger.info("SubtitleGenerator initialized")

    async def generate_subtitles(self, word_timestamps: Sequence[Tuple[float, float, str]], output_file: str) -> str:
        if not word_timestamps:
            raise ValueError("word_timestamps cannot be empty")
        if not output_file:
            raise ValueError("output_file cannot be empty")
        self.progress_manager.start_task("Generating subtitles")

        # Modify the output file name
        base_name = os.path.splitext(os.path.splitext(output_file)[0])[0]
        output_file = f"{base_name}.srt"

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

    def _group_words_into_segments(
        self, word_timestamps: Sequence[Tuple[float, float, str]]
    ) -> List[Tuple[float, float, str]]:
        """Group words into subtitle segments based on timing constraints and sentence structure."""
        if not word_timestamps:
            return []  # Return an empty list if word_timestamps is empty
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
                    if i - len(second_part) >= 0:
                        segments.append(
                            (current_start_time, word_timestamps[i - len(second_part)][1], " ".join(first_part))
                        )
                    else:
                        segments.append((current_start_time, last_end_time, " ".join(first_part)))

                    # Start a new segment with the second part
                    current_segment = second_part
                    if i - len(second_part) + 1 < len(word_timestamps):
                        current_start_time = word_timestamps[i - len(second_part) + 1][0]
                    else:
                        current_start_time = last_end_time
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
        for i in range(len(words) - 1, -1, -1):
            if words[i][-1] in self.END_SENTENCE_PUNCTUATION:
                return i + 1

        for i in range(len(words) - 1, -1, -1):
            if words[i].endswith(","):
                return i + 1

        return len(words) // 2

    async def _write_srt_file(self, segments: List[Tuple[float, float, str]], output_file: str):
        try:
            total_segments = len(segments)
            self.progress_manager.start_task(f"Writing {total_segments} subtitle segments", total=total_segments)
            async with aiofiles.open(output_file, "x") as f:
                for i, (start_time, end_time, text) in enumerate(segments, 1):
                    await f.write(f"{i}\n")
                    await f.write(f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n")
                    await f.write(f"{text}\n\n")
                    self.progress_manager.update_progress(1)
            self.progress_manager.complete_task("Subtitle file written")
        except Exception as e:
            logger.error(f"Error writing to file: {str(e)}")
            self.progress_manager.fail_task("Failed to write subtitle file")
            raise

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")
