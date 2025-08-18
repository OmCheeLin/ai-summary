import os
import shutil
import uuid
from pathlib import Path

from loguru import logger
import subprocess

from util.common.constants import Constants
from util.common.time_util import ms_to_format_str, format_str_to_ms


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


def do_mux_av(input_video, input_audio, output_file):
    """
    将视频流和音频流合并为一个文件（不重新编码）

    Args:
        input_video (str): 视频文件路径（无音频）
        input_audio (str): 音频文件路径（无视频）
        output_file (str): 输出合并后的文件路径
    """
    cmd = [
        Constants.FFMPEG_PATH,
        '-i', input_video,
        '-i', input_audio,
        '-c', 'copy',  # 不重新编码
        output_file
    ]

    try:
        logger.info("合并视频和音频中...")
        subprocess.run(cmd, check=True)
        logger.info(f"合并完成！输出文件: {output_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"合并失败: {e}")


def mux_av(video_id):
    # 动态匹配以 video_id 开头的 mp4 / m4a 文件
    video_file = next(Path(Constants.TMP_DIR).glob(f"{video_id}*.mp4"), None)
    audio_file = next(Path(Constants.TMP_DIR).glob(f"{video_id}*.m4a"), None)
    if not video_file or not audio_file:
        raise FileNotFoundError(f"未找到视频或音频文件: {video_file}, {audio_file}")
    output_mux_path = Path(Constants.VIDEO_UPLOAD_DIR) / f'{video_id}.mp4'
    do_mux_av(str(video_file), str(audio_file), str(output_mux_path))
    return output_mux_path


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


def filter_keyframe(file_path, part_begin_time, part_end_time):
    keyframe_dir = get_keyframe(file_path, part_begin_time, part_end_time)
    # 确保 keyframe_dir 不为空
    keyframe_files = sorted(Path(keyframe_dir).glob("*.jpg"))
    if not keyframe_files:
        raise FileNotFoundError("没有找到关键帧图片")
    # 取第一张关键帧
    first_frame = keyframe_files[0]
    # 生成新的 UUID 文件名
    img_name = f"{uuid.uuid4()}.png"
    output_img = Path(Constants.IMG_DIR) / img_name
    output_img.parent.mkdir(parents=True, exist_ok=True)  # 确保目录存在
    # 将图片拷贝并改名为 PNG
    shutil.copy(first_frame, output_img)
    # 删除 keyframe_dir
    shutil.rmtree(keyframe_dir, ignore_errors=True)
    # 返回可访问路径
    return f"/upload/img/{img_name}"


def get_keyframe(input_file, part_begin_time, part_end_time):
    """
    test:
    D:\python_workspace\tecent\plugin\ffmpeg-win64\bin\ffmpeg.exe -skip_frame nokey -i output.mp4 -vsync 0 -frame_pts 1 D:\python_workspace\b\%d.jpg
    D:\python_workspace\tecent\plugin\ffmpeg-win64\bin\ffmpeg.exe -i output.mp4 -vf "select='eq(pict_type\,I)*between(t\,0\,10)'" -vsync vfr D:\python_workspace\b\keyframes_%03d.jpg
    """
    uid = str(uuid.uuid4())
    keyframe_dir = Path(Constants.TMP_DIR) / uid
    keyframe_dir.mkdir(parents=True, exist_ok=True)
    middle_time = str((part_begin_time + part_end_time) // 2)
    # 输出文件路径模板
    output_pattern = str(keyframe_dir / f"{middle_time}_%d.jpg")
    cmd_keyframe = [
        Constants.FFMPEG_PATH,
        '-i', str(input_file),
        "-vf", f"select=eq(pict_type\\,I)*between(t\\,{part_begin_time}\\,{part_end_time})",
        "-vsync", "vfr",
        output_pattern
    ]
    logger.info(f"get_keyframe: {part_begin_time}, {part_end_time}")
    subprocess.run(cmd_keyframe, check=True)
    return str(keyframe_dir)

