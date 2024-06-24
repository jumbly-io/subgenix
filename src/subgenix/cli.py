import asyncio
import click
from loguru import logger
from .audio_extractor import extract_audio
from .speech_to_text import transcribe_audio
from .subtitle_generator import generate_subtitles
from .cache_manager import CacheManager
from .progress_display import ProgressDisplay


@click.command()
@click.argument("video_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output SRT file path")
@click.option("--language", "-l", default=None, help="Override auto-detected language")
@click.option("--translate-to", "-t", default=None, help="Translate subtitles to this language")
@click.option("--show-progress/--hide-progress", default=True, help="Show/hide progress bar")
@click.option("--structured-logging", is_flag=True, help="Enable structured logging output")
@click.option("--use-gpu", is_flag=True, help="Use GPU for acceleration if available")
async def main(video_file, output, language, translate_to, show_progress, structured_logging, use_gpu):
    """Generate subtitles for a video file."""
    if structured_logging:
        logger.add("subgenix.log", serialize=True)
    else:
        logger.add("subgenix.log", format="{time} {level} {message}", level="INFO")

    logger.info(f"Processing video file: {video_file}")

    cache_manager = CacheManager(video_file)
    progress_display = ProgressDisplay(show_progress)

    try:
        # Extract audio
        audio_file = await extract_audio(video_file, cache_manager, progress_display)

        # Transcribe audio
        transcription = await transcribe_audio(audio_file, language, use_gpu, progress_display)

        # Generate subtitles
        srt_file = await generate_subtitles(transcription, output or f"{video_file}.srt", progress_display)

        if translate_to:
            # TODO: Implement translation
            pass

        logger.info(f"Subtitles generated successfully: {srt_file}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    asyncio.run(main())
