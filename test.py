import requests
import json
import time
from loguru import logger


# 提交文件转写任务，包含待转写文件url列表
def submit_task(api_key: str, file_urls: list, language_hints=None) -> str:
    if language_hints is None:
        language_hints = ["zh", "en"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    data = {
        "model": "paraformer-v2",
        "input": {"file_urls": file_urls},
        "parameters": {
            "channel_id": [0],
            "language_hints": language_hints,
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
        return ""


# 循环查询任务状态直到成功
def wait_for_complete(api_key: str, task_id: str):
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
                return response.json()['output']['results']
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


# 下载并解析转写结果
def download_transcription(transcription_url: str):
    response = requests.get(transcription_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        logger.error(f"transcription_url 下载失败，状态码：{response.status_code}")
        return None


def audio_to_text(file_urls: list):
    api_key = "sk-f82e5e0aae6543fd91fb2186bf3299a9"
    task_id = submit_task(api_key=api_key, file_urls=file_urls)
    logger.info(f"task_id: {task_id}")
    results = wait_for_complete(api_key=api_key, task_id=task_id)
    if results:
        for item in results:
            transcription_url = item['transcription_url']
            logger.info(f"transcription_url: {transcription_url}")
            data = download_transcription(transcription_url)
            if data:
                return json.dumps(data, ensure_ascii=False, indent=2)
    else:
        logger.error("未能获取结果")
