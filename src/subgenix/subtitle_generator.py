from typing import List, Tuple
import aiofiles
import os


class SubtitleGenerator:
    MAX_SEGMENT_DURATION = 5.0  # Maximum duration for a single subtitle
    MAX_PAUSE_DURATION = 2.0  # Maximum duration of a pause before creating a new subtitle
    END_SENTENCE_PUNCTUATION = ".!?"  # Punctuation that typically ends a sentence

    def __init__(self):
        pass

    async def generate_subtitles(self, word_timestamps: List[Tuple[float, float, str]], output_file: str) -> str:
        """
        Generate subtitles from word timestamps and write them to an SRT file.

        Args:
            word_timestamps: A list of tuples containing (start_time, end_time, word).
            output_file: The path to the output file.

        Returns:
            The path to the generated SRT file.

        Raises:
            Exception: If there's an error during subtitle generation.
        """
        subtitle_segments = self._group_words_into_segments(word_timestamps)
        srt_filename = self._get_srt_filename(output_file)
        await self._write_srt_file(subtitle_segments, srt_filename)
        return srt_filename

    def _get_srt_filename(self, output_file: str) -> str:
        """Convert the output filename to an SRT filename."""
        base_name = os.path.splitext(output_file)[0]
        return f"{base_name}.srt"

    def _group_words_into_segments(self, word_timestamps: List[Tuple[float, float, str]]) -> List[Tuple[float, float, str]]:
        """Group words into subtitle segments based on timing constraints and sentence structure."""
        segments = []
        current_segment = []
        current_start_time = word_timestamps[0][0]

        for start, end, word in word_timestamps:
            current_segment.append(word)
            if end - current_start_time >= self.MAX_SEGMENT_DURATION or len(current_segment) >= 10:
                segments.append((current_start_time, end, " ".join(current_segment)))
                current_segment = []
                current_start_time = end

        # Add any remaining words
        if current_segment:
            segments.append((current_start_time, word_timestamps[-1][1], " ".join(current_segment)))

        return segments

    def _find_split_index(self, words: List[str]) -> int:
        """Find the best index to split a list of words, preferring sentence boundaries."""
        for i in range(len(words) - 1, -1, -1):
            if words[i][-1] in self.END_SENTENCE_PUNCTUATION:
                return i + 1  # Split after the punctuation

        for i in range(len(words) - 1, -1, -1):
            if words[i].endswith(","):
                return i + 1  # Split after the comma

        return len(words) // 2

    async def _write_srt_file(self, segments: List[Tuple[float, float, str]], output_file: str):
        """Write the subtitle segments to an SRT file."""
        async with aiofiles.open(output_file, "w") as f:
            for i, (start_time, end_time, text) in enumerate(segments, 1):
                await f.write(f"{i}\n")
                await f.write(f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n")
                await f.write(f"{text}\n\n")

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format time in seconds to SRT time format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")
