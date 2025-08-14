import json
import uuid
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
import shutil
import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi import Form

from config.config import get_yaml_config
from service.workflow import analyse_workflow
from util.constants import Constants

app = FastAPI()
Constants.init_filepath(os.getcwd())
# 挂载静态目录，公开访问上传的视频、截取图片
app.mount("/upload/video", StaticFiles(directory="upload/video"), name="video")
app.mount("/upload/img", StaticFiles(directory="upload/img"), name="img")
# 挂载静态资源目录（用于加载 CSS、JS、图片等）
app.mount("/ui", StaticFiles(directory="ui"), name="ui")
# 设置模板目录（HTML 页面）
templates = Jinja2Templates(directory="ui")

@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def is_extension_allowed(filename: str) -> bool:
    ext = filename.split(".")[-1].lower()
    return ext in Constants.ALLOWED_VIDEO_EXTENSIONS


@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    if not is_extension_allowed(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file extension.")

    # 保存视频
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(Constants.VIDEO_UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "status": "success",
        "filename": filename,
        "video_url": f"/upload/video/{filename}"
    }


@app.post("/analyse/")
async def analyse(filename: str = Form(...)):
    all_result_json = analyse_workflow(filename)
    # 渲染模板成 HTML 字符串
    # with open("result.json", "r", encoding="utf-8") as f:
    #     all_result_json = json.load(f)
    html_content = templates.get_template("result_section.html").render(**all_result_json)
    return JSONResponse({"html": html_content})


if __name__ == "__main__":
    yaml_config = get_yaml_config()
    uvicorn.run(
        "main:app",
        port=8765,
        log_level="debug",
        reload=True,
    )