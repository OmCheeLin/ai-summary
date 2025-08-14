import alibabacloud_oss_v2 as oss
from loguru import logger
from config.config import get_oss_client

def upload_audio_to_oss(local_file_path, object_key, bucket_name="wangyi-mp3") -> str:
    client = get_oss_client()
    # 读取本地音频文件
    with open(local_file_path, 'rb') as f:
        data = f.read()
    # 执行上传操作
    result = client.put_object(oss.PutObjectRequest(
        bucket=bucket_name,
        key=object_key,
        body=data,
    ))
    if result.status_code != 200:
        logger.error(f'上传失败！status code: {result.status_code}')
        return ""
    url = get_audio_download_url(client, object_key)
    logger.info(f'上传成功！status_code: {result.status_code}, request_id: {result.request_id}, etag: {result.etag}')
    return url

def get_audio_download_url(client, object_key, bucket_name="wangyi-mp3") -> str:
    # 生成预签名的GET请求
    pre_result = client.presign(
        oss.GetObjectRequest(
            bucket=bucket_name,  # 指定存储空间名称
            key=object_key,  # 指定对象键名
        )
    )
    # 打印预签名请求的方法、过期时间和URL
    logger.info(f'method: {pre_result.method}, expiration: {pre_result.expiration.strftime("%Y-%m-%dT%H:%M:%S.000Z")}, url: {pre_result.url}')
    return pre_result.url