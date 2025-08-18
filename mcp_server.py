import uuid

from mcp.server.fastmcp import FastMCP
import json

from service.workflow import analyse_workflow
from util.common.docx_util import generate_docx

mcp = FastMCP("视频图文报告生成服务")

@mcp.tool()
def video_summary(video_url: str) -> str:
    """
    获取当前设备的系统信息。
    :param video_url: 输入视频的URL（仅支持哔哩哔哩）
    Returns:
        str: 返回图文报告docx下载链接
    """
    all_result_json = analyse_workflow(video_url)
    uid = f'{uuid.uuid4()}.docx'
    generate_docx(all_result_json, uid)
    resp = {'download_docx_link': f'http://localhost:8765/download-docx/{uid}'}
    return json.dumps(resp)


if __name__ == "__main__":
    mcp.run(transport="stdio")
