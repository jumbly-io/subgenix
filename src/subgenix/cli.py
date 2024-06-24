import asyncio
import click
from loguru import logger
from .audio_extractor import AudioExtractor
from .audio_transcriber import AudioTranscriber
from .subtitle_generator import SubtitleGenerator
from .cache_manager import CacheManager
from .progress_manager import ProgressManager

@click.command()
@click.argument("video_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output SRT file path")
@click.option("--language", "-l", default=None, help="Override auto-detected language")
@click.option("--model", "-m", default="base", type=click.Choice(["tiny", "base", "small", "medium", "large"]), help="Whisper model size")
@click.option("--show-progress/--hide-progress", default=True, help="Show/hide progress bar")
@click.option("--structured-logging", is_flag=True, help="Enable structured logging output")
@click.option("--use-gpu", is_flag=True, help="Use GPU for acceleration if available")
async def main(video_file, output, language, model, show_progress, structured_logging, use_gpu):
    """Generate subtitles for a video file."""
    if structured_logging:
        logger.add("subgenix.log", serialize=True)
    else:
        logger.add("subgenix.log", format="{time} {level} {message}", level="INFO")

    logger.info(f"Processing video file: {video_file}")

    # Instantiate objects from classes
    cache_manager = CacheManager(video_file)
    progress_manager = ProgressManager(show_progress)
    audio_extractor = AudioExtractor(cache_manager, progress_manager)
    audio_transcriber = AudioTranscriber(progress_manager, model)
    subtitle_generator = SubtitleGenerator(progress_manager)

    try:
        # Extract audio
        audio_file, duration = await audio_extractor.process_video(video_file)

        # Transcribe audio with word-level timestamps
        word_timestamps = await audio_transcriber.transcribe_audio(audio_file, language, use_gpu)

        # Generate subtitles
        output_file = output or f"{video_file}.srt"
        srt_file = await subtitle_generator.generate_subtitles(word_timestamps, output_file)

        logger.info(f"Subtitles generated successfully: {srt_file}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise click.ClickException(str(e))
    finally:
        # Clean up any temporary files
        await cache_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
