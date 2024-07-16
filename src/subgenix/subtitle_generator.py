from typing import List, Tuple, Sequence, Optional
from loguru import logger
import aiofiles
from .progress_manager import ProgressManager
import os
import asyncio

class SubtitleGenerator:
    DEFAULT_MAX_SEGMENT_DURATION = 5.0
    DEFAULT_MAX_PAUSE_DURATION = 2.0
    END_SENTENCE_PUNCTUATION = ".!?"

    def __init__(self, progress_manager: ProgressManager, 
                 max_segment_duration: float = DEFAULT_MAX_SEGMENT_DURATION,
                 max_pause_duration: float = DEFAULT_MAX_PAUSE_DURATION):
        self.progress_manager = progress_manager
        self.max_segment_duration = max_segment_duration
        self.max_pause_duration = max_pause_duration
        logger.info("SubtitleGenerator initialized")

    async def generate_subtitles(self, word_timestamps: Sequence[Tuple[float, float, str]], 
                                 output_file: str, 
                                 font_name: str = 'Arial',
                                 font_size: int = 16,
                                 font_color: str = 'white',
                                 font_style: str = 'normal',
                                 output_format: str = 'srt') -> str:
        """
        Generate subtitles from word timestamps and write them to a file.

        Args:
            word_timestamps: A sequence of tuples containing (start_time, end_time, word).
            output_file: The path to the output file.
            font_name: The name of the font to use.
            font_size: The size of the font.
            font_color: The color of the font.
            font_style: The style of the font ('normal', 'italic', or 'bold').
            output_format: The format of the output file ('srt' or 'vtt').

        Returns:
            The path to the generated subtitle file.

        Raises:
            Exception: If there's an error during subtitle generation.
        """
        self.progress_manager.start_task("Generating subtitles")
        logger.info(f"Generating subtitles for output file: {output_file}")
        try:
            word_timestamps = await self._preprocess_text(word_timestamps)
            subtitle_segments = await self._group_words_into_segments(word_timestamps)
            subtitle_filename = self._get_subtitle_filename(output_file, output_format)
            
            if output_format == 'srt':
                await self._write_srt_file(subtitle_segments, subtitle_filename, font_name, font_size, font_color, font_style)
            elif output_format == 'vtt':
                await self._write_vtt_file(subtitle_segments, subtitle_filename, font_name, font_size, font_color, font_style)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            self.progress_manager.complete_task("Subtitles generated")
            return subtitle_filename
        except Exception as e:
            logger.exception(f"Error generating subtitles: {str(e)}")
            self.progress_manager.fail_task("Subtitle generation failed")
            raise

    def _get_subtitle_filename(self, output_file: str, format: str) -> str:
        """Convert the output filename to a subtitle filename."""
        base_name = os.path.splitext(output_file)[0]
        return f"{base_name}.{format}"

    async def _preprocess_text(self, word_timestamps: Sequence[Tuple[float, float, str]]) -> Sequence[Tuple[float, float, str]]:
        """Preprocess the text in word timestamps."""
        return [(start, end, word.strip().lower()) for start, end, word in word_timestamps if word.strip()]

    async def _group_words_into_segments(
        self, word_timestamps: Sequence[Tuple[float, float, str]]
    ) -> List[Tuple[float, float, str]]:
        """Group words into subtitle segments based on timing constraints and sentence structure."""
        segments = []
        current_segment = []
        current_start_time = word_timestamps[0][0]
        last_end_time = word_timestamps[0][1]

        for i, (start, end, word) in enumerate(word_timestamps):
            current_segment.append(word)
            segment_duration = end - current_start_time
            pause_duration = start - last_end_time

            if segment_duration >= self.max_segment_duration or pause_duration >= self.max_pause_duration:
                split_index = self._find_split_index(current_segment)
                if split_index > 0:
                    first_part = current_segment[:split_index]
                    second_part = current_segment[split_index:]

                    segments.append(
                        (current_start_time, word_timestamps[i - len(second_part)][1], " ".join(first_part))
                    )

                    current_segment = second_part
                    current_start_time = word_timestamps[i - len(second_part) + 1][0]
                else:
                    segments.append((current_start_time, end, " ".join(current_segment)))
                    current_segment = []
                    current_start_time = end

            last_end_time = end

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

    async def _write_srt_file(self, segments: Sequence[Tuple[float, float, str]], output_file: str,
                              font_name: str, font_size: int, font_color: str, font_style: str):
        """Write the subtitle segments to an SRT file."""
        total_segments = len(segments)
        self.progress_manager.start_task(f"Writing {total_segments} subtitle segments", total=total_segments)
        try:
            async with aiofiles.open(output_file, "w") as f:
                for i, (start_time, end_time, text) in enumerate(segments, 1):
                    await f.write(f"{i}\n")
                    await f.write(f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n")
                    styled_text = self._apply_style(text, font_name, font_size, font_color, font_style)
                    await f.write(f"{styled_text}\n\n")
                    self.progress_manager.update_progress(1)
        except IOError as e:
            logger.error(f"Error writing SRT file: {str(e)}")
            raise
        finally:
            self.progress_manager.complete_task("Subtitle file written")

    async def _write_vtt_file(self, segments: Sequence[Tuple[float, float, str]], output_file: str,
                              font_name: str, font_size: int, font_color: str, font_style: str):
        """Write the subtitle segments to a WebVTT file."""
        total_segments = len(segments)
        self.progress_manager.start_task(f"Writing {total_segments} subtitle segments", total=total_segments)
        try:
            async with aiofiles.open(output_file, "w") as f:
                await f.write("WEBVTT\n\n")
                for i, (start_time, end_time, text) in enumerate(segments, 1):
                    await f.write(f"{self._format_time_vtt(start_time)} --> {self._format_time_vtt(end_time)}\n")
                    styled_text = self._apply_style(text, font_name, font_size, font_color, font_style)
                    await f.write(f"{styled_text}\n\n")
                    self.progress_manager.update_progress(1)
        except IOError as e:
            logger.error(f"Error writing VTT file: {str(e)}")
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

    @staticmethod
    def _format_time_vtt(seconds: float) -> str:
        """Format time in seconds to WebVTT time format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

    @staticmethod
    def _apply_style(text: str, font_name: str, font_size: int, font_color: str, font_style: str) -> str:
        """Apply styling to the subtitle text."""
        style = f'<font face="{font_name}" size="{font_size}" color="{font_color}">'
        if font_style == 'italic':
            style += '<i>'
        elif font_style == 'bold':
            style += '<b>'
        
        styled_text = f"{style}{text}"
        
        if font_style in ['italic', 'bold']:
            styled_text += '</i>' if font_style == 'italic' else '</b>'
        styled_text += '</font>'
        
        return styled_text
