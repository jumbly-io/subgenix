from loguru import logger

logger.add("file.log", format="{time} {level} {message}", level="INFO")


def main():
    logger.info("This is an info message")


if __name__ == "__main__":
    main()
