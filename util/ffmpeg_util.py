import os
import uuid
from pathlib import Path

from loguru import logger
import subprocess

from util.constants import Constants


def do_demux_av(input_file, output_video, output_audio):
    # 提取视频流（不带音频）
    cmd_video = [
        Constants.FFMPEG_PATH,
        '-i', input_file,
        '-an',               # 去掉音频
        '-c:', 'copy',        # 不重新编码
        output_video
    ]

    # 提取音频流（不带视频）
    cmd_audio = [
        Constants.FFMPEG_PATH,
        '-i', input_file,
        '-vn',               # 去掉视频
        '-c', 'copy',        # 不重新编码
        output_audio
    ]

    try:
        logger.info("提取视频流中...")
        subprocess.run(cmd_video, check=True)
        logger.info("提取音频流中...")
        subprocess.run(cmd_audio, check=True)
        logger.info(f"分流完成！【output_video】{output_video}  【output_audio】{output_audio}")
    except subprocess.CalledProcessError as e:
        logger.error("发生错误:", e)


def demux_av(input_file_path, filename):
    filename = filename.split(".")[0]
    output_video = os.path.normpath(os.path.join(Constants.TMP_DIR, f'{filename}_only_video.mp4'))
    output_audio = os.path.normpath(os.path.join(Constants.TMP_DIR, f'{filename}_only_audio.m4a'))
    do_demux_av(input_file_path, output_video, output_audio)
    return output_video, output_audio


def screenshot(input_file, timepoint):
    img_name = f'{uuid.uuid4()}.png'
    output_img = str(Constants.IMG_DIR / Path(img_name))
    cmd_screenshot = [
        Constants.FFMPEG_PATH,
        '-ss', str(timepoint),
        '-i', str(input_file),
        '-frames:v', "1",
        str(output_img)
    ]
    subprocess.run(cmd_screenshot, check=True)
    logger.info("截取视频图片")
    return f"/upload/img/{img_name}"
