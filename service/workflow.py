import json
import os
import re
from pathlib import Path

from util.asr_util import audio_to_text
from util.common.constants import Constants
from util.ffmpeg_util import demux_av, screenshot, filter_keyframe
from util.llm_util import get_llm_summary, get_llm_group_sentences
from util.oss_util import upload_audio_to_oss
from loguru import logger

from util.common.time_util import ms_to_format_str, format_str_to_ms
from util.ytdlp_util import download_video_from_url


def analyse_workflow(filename):
    file_path = None
    if not is_url(filename):
        file_path = os.path.join(Constants.VIDEO_UPLOAD_DIR, filename)
        # ffmpeg 分离音频、视频
        output_video, output_audio = demux_av(file_path, filename)
    else:
        output_video, output_audio = download_video_from_url(filename)
        file_path = output_video
    # 上传音频到 oss
    download_link = upload_audio_to_oss(output_audio, Path(output_video).name)

    # 送入 ASR
    full_text, filtered_sentences = audio_to_text([download_link])
    # 生成【全文摘要】和【全文亮点】
    summary_json = get_llm_summary(full_text)
    # 生成【分段总结】
    result_group_json = group_sentences(file_path, full_text, filtered_sentences)
    # 组合 summary_json 和 result_group_json
    all_result_json = assembly_result(summary_json, result_group_json)
    # 保存到文件 (debug)
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(all_result_json, f, ensure_ascii=False, indent=4)
    # 删除本地文件
    Path(output_audio).unlink(missing_ok=True)
    Path(output_video).unlink(missing_ok=True)
    return all_result_json


def group_sentences(file_path, full_text, filtered_sentences):
    """
    Group sentences into separate sentences.
    :param file_path: 上传视频的URL
    :param full_text: 视频文本全文
    :param filtered_sentences: 单句列表（包含 begin_time 和 end_time）
    :return:
    """
    new_filtered_sentences = []
    for s in filtered_sentences:
        new_s = {
            'text': s.get('text'),
            'sentence_id': s.get('sentence_id')
        }
        new_filtered_sentences.append(new_s)
    query_text = f"""视频文本全文：{full_text}\n
               单句列表：\n{new_filtered_sentences}
               """
    group_json = get_llm_group_sentences(query_text)
    # 组装结果
    result_group_json = []
    for part in group_json['分段总结']:
        part_begin_time = find_by_sentence_id(min(part['sentence_ids']), filtered_sentences, 'begin_time')
        part_end_time = find_by_sentence_id(max(part['sentence_ids']), filtered_sentences, 'end_time')
        middle_time = ms_to_format_str( (format_str_to_ms(part_begin_time) + format_str_to_ms(part_end_time)) // 2 )
        img_url = screenshot(file_path, str(middle_time))
        # img_url = filter_keyframe(file_path, format_str_to_ms(part_begin_time), format_str_to_ms(part_end_time))
        part_result = {
            'title': part['title'],
            'summary': part['summary'],
            'part_begin_time': part_begin_time,
            'part_end_time': part_end_time,
            'img_url': img_url,
            'sentences': get_sentences(part['sentence_ids'], filtered_sentences)
        }
        result_group_json.append(part_result)
    return result_group_json


def assembly_result(summary_json, result_group_json):
    """
    summary_json = {
        "summary": "全文摘要",
        "highlights": [
            "亮点1...",
            "亮点2...",
            "亮点3...",
        ]
    }
    """
    all_result = summary_json
    all_result['groups'] = result_group_json
    return all_result


def find_by_sentence_id(sentence_id, filtered_sentences, key):
    for s in filtered_sentences:
        if s['sentence_id'] == sentence_id:
            return s[key]
    logger.error(f"没有在 filtered_sentences 找到 sentence_id：{sentence_id}")
    return None


def get_sentences(sentence_ids, filtered_sentences):
    new_sentences = []
    for s in filtered_sentences:
        if s['sentence_id'] in sentence_ids:
            new_sentences.append(s)
    return new_sentences


def is_url(s: str) -> bool:
    pattern = re.compile(r'^(https?)://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
    return bool(pattern.match(s))