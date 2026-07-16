"""AI 生图路由 — 宣传海报生成"""

import json
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import httpx
from io import BytesIO

from app.config import settings

router = APIRouter(prefix="/ai", tags=["AI 生图"])


@router.get("/image")
async def generate_image(
    prompt: str = Query(..., description="图片提示词"),
):
    """
    文生图接口：根据提示词生成宣传海报图片

    基于阿里云百炼 qwen-image-plus 模型

    示例提示词：
    生成一张宣传瑜伽馆的海报，名字叫"伽云瑜伽"，地址在山东省济南市长清区，负责人为张三，手机号为13112311211
    """
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"

    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.IMAGE_MODEL,
        "input": {
            "prompt": prompt,
        },
        "parameters": {
            "size": "1024*1024",
            "n": 1,
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # 第一步：提交任务
            response = await client.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code != 200:
                return {"error": f"图片生成请求失败: {response_data}"}

            task_id = response_data.get("output", {}).get("task_id")
            if not task_id:
                return {"error": "未能获取任务ID"}

            # 第二步：轮询获取结果
            status_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
            import asyncio

            for _ in range(30):  # 最多等待 30 次
                await asyncio.sleep(2)
                status_response = await client.get(status_url, headers=headers)
                status_data = status_response.json()
                task_status = status_data.get("output", {}).get("task_status")

                if task_status == "SUCCEEDED":
                    image_url = status_data.get("output", {}).get("results", [{}])[0].get("url")
                    if image_url:
                        # 下载图片并返回
                        img_response = await client.get(image_url)
                        img_bytes = BytesIO(img_response.content)
                        return StreamingResponse(
                            img_bytes,
                            media_type="image/png",
                            headers={
                                "Content-Disposition": f"attachment; filename=generated_image.png"
                            }
                        )
                    break
                elif task_status == "FAILED":
                    return {"error": f"图片生成失败: {status_data}"}

            return {"error": "图片生成超时，请稍后重试"}

        except httpx.TimeoutException:
            return {"error": "图片生成请求超时"}
        except Exception as e:
            return {"error": f"图片生成出错: {str(e)}"}