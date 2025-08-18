import re
import json


def extract_json_from_text(text):
    # 尝试从 ```json ``` 中提取
    code_block_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if code_block_match:
        json_str = code_block_match.group(1).strip()
    else:
        # 如果没有 ```json```，尝试提取裸 JSON 对象
        json_match = re.search(r"({.*})", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            raise ValueError("未找到 JSON 内容")
    # 解析 JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}")