import os
from loguru import logger

class Constants:

    VIDEO_UPLOAD_DIR = "upload/video"
    IMG_DIR = "upload/img"

    MAX_UPLOAD_SIZE_MB = 10000

    ALLOWED_VIDEO_EXTENSIONS = [
        "mp4", "mov", "avi", "mkv", "flv", "wmv", "webm",
        "mpeg", "mpg", "3gp", "ts", "m4v"
    ]

    FFMPEG_PATH = r"plugin/ffmpeg-win64/bin/ffmpeg.exe"

    TMP_DIR = "tmp"

    @staticmethod
    def init_filepath(base_dir):
        Constants.VIDEO_UPLOAD_DIR = os.path.normpath(os.path.join(base_dir, Constants.VIDEO_UPLOAD_DIR))
        Constants.IMG_DIR = os.path.normpath(os.path.join(base_dir, Constants.IMG_DIR))
        Constants.TMP_DIR = os.path.normpath(os.path.join(base_dir, Constants.TMP_DIR))
        Constants.FFMPEG_PATH = os.path.normpath(os.path.join(base_dir, Constants.FFMPEG_PATH))

        os.makedirs(Constants.VIDEO_UPLOAD_DIR, exist_ok=True)
        os.makedirs(Constants.IMG_DIR, exist_ok=True)
        os.makedirs(Constants.TMP_DIR, exist_ok=True)

        logger.info("路径初始化完成!")
        logger.info(f"VIDEO_UPLOAD_DIR: {Constants.VIDEO_UPLOAD_DIR}")
        logger.info(f"IMG_DIR: {Constants.IMG_DIR}")
        logger.info(f"TMP_DIR: {Constants.TMP_DIR}")
        logger.info(f"FFMPEG_PATH: {Constants.FFMPEG_PATH}")
