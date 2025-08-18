import requests
import json
import time
from loguru import logger

from config.config import get_llm_api_key
from util.common.time_util import ms_to_format_str


# 提交文件转写任务，包含待转写文件url列表
def submit_task(apikey, file_urls) -> str:
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    data = {
        "model": "paraformer-v2",
        "input": {"file_urls": file_urls},
        "parameters": {
            "channel_id": [0],
            "language_hints": ["zh", "en"],
            "vocabulary_id": "vocab-Xxxx",
        },
    }
    # 录音文件转写服务url
    service_url = (
        "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
    )
    response = requests.post(
        service_url, headers=headers, data=json.dumps(data)
    )

    # 打印响应内容
    if response.status_code == 200:
        return response.json()["output"]["task_id"]
    else:
        logger.error("task failed!")
        logger.error(response.json())
        return None


# 循环查询任务状态直到成功
def wait_for_complete(api_key, task_id):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }

    pending = True
    while pending:
        # 查询任务状态服务url
        service_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        response = requests.post(
            service_url, headers=headers
        )
        if response.status_code == 200:
            status = response.json()['output']['task_status']
            if status == 'SUCCEEDED':
                logger.info("task succeeded!")
                pending = False
                return response.json()['output']['results'][0]['transcription_url']
            elif status == 'RUNNING' or status == 'PENDING':
                pass
            else:
                logger.error("task failed!")
                pending = False
        else:
            logger.error("query failed!")
            pending = False
        logger.info(response.json())
        time.sleep(1)

def download_and_extract_text(result_url):
    # 请求下载JSON
    response = requests.get(result_url)
    response.raise_for_status()  # 如果下载失败会抛异常
    data = response.json()  # 解析JSON
    # 文本在 transcripts 里，每个元素里有 text 字段
    transcripts = []
    if len(data.get('transcripts', [])) > 0:
        transcripts = data.get('transcripts', [])[0]
    full_text = transcripts.get('text', '')
    sentences = transcripts.get('sentences', [])

    # 只提取需要的字段，去掉 words
    filtered_sentences = []
    for s in sentences:
        begin_time = ms_to_format_str(s.get('begin_time'))
        end_time = ms_to_format_str(s.get('end_time'))
        filtered_sentence = {
            'begin_time': begin_time,
            'end_time': end_time,
            'text': s.get('text'),
            'sentence_id': s.get('sentence_id')
        }
        filtered_sentences.append(filtered_sentence)
    return full_text, filtered_sentences


def audio_to_text(file_urls):
    api_key = get_llm_api_key()
    task_id = submit_task(api_key, file_urls)
    result_url = wait_for_complete(api_key, task_id)
    full_text, filtered_sentences = download_and_extract_text(result_url)
    return full_text, filtered_sentences


if __name__ == "__main__":
    url = 'https://wangyi-mp3.oss-cn-beijing.aliyuncs.com/example_audio.mp3?Expires=1755015395&OSSAccessKeyId=TMP.3KmVBHSWrdjp4LnDDreGpbZo2CboCL85keC3NZUWTTByEak2Z98G5wwDLJzxRvasYRCKTT1GVChHVRonmdL74CWS6te3cQ&Signature=6zOis2WZBhcyT86PpmFmnDLI8T0%3D'
    full_text, filtered_sentences = audio_to_text([url])
    print(full_text)
    print()
    print(filtered_sentences)