import re
import subprocess
import uuid
from pathlib import Path

from util.common.constants import Constants
from loguru import logger

from util.ffmpeg_util import mux_av


# 仅支持 bilibili
def download_video_from_url(video_url):
    video_url = parse_url(video_url)
    video_id = str(uuid.uuid4())
    output_path = Path(Constants.TMP_DIR) / f"{video_id}.%(ext)s"
    ytdlp_cmd = [
        Constants.YTDLP_PATH,
        "-o", str(output_path),
        str(video_url)
    ]
    try:
        logger.info("从 url 下载视频中...")
        subprocess.run(ytdlp_cmd, check=True)
        logger.info(f"视频 url 下载完成")
        # 无需合并视频和音频
        tmp_dir = Path(Constants.TMP_DIR)
        mp4_file = next(tmp_dir.glob(f"{video_id}*.mp4"), None)
        m4a_file = next(tmp_dir.glob(f"{video_id}*.m4a"), None)

        if not mp4_file and not m4a_file:
            raise FileNotFoundError("未找到对应的 mp4 或 m4a 文件")
        # 返回绝对路径
        return str(mp4_file.resolve()), str(m4a_file.resolve())
    except subprocess.CalledProcessError as e:
        raise Exception(f"发生错误: {e}")


def parse_url(url):
    """
    url例子：
    https://www.bilibili.com/video/BV1Eb411u7Fw?t=1.0
    https://www.bilibili.com/video/BV1Eb411u7Fw?t=0.8&p=2
    """
    # 判断 URL 中是否已经有 &p= 参数
    parsed_url = url
    if re.search(r'([&?])p=\d+', url):
        logger.info(f"解析后的 url: {parsed_url}")
        return parsed_url
    # 如果没有 &p= 参数，判断 URL 是否有 ?，然后拼接 &p=1 或 ?p=1
    if '?' in url:
        parsed_url = url + '&p=1'
    else:
        parsed_url = url + '?p=1'
    logger.info(f"解析后的 url: {parsed_url}")
    return parsed_url


if __name__ == "__main__":
    Constants.init_filepath(r"D:\python_workspace\tecent")
    download_video_from_url("https://www.bilibili.com/video/BV1Eb411u7Fw?t=1.0")