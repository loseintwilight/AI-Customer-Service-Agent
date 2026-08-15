"""FastAPI 应用入口"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat_router, image_router, question_router, bi_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("=" * 50)
    logger.info("AI 智能客服综合平台启动中...")
    logger.info(f"服务端口: {settings.SERVER_PORT}")
    logger.info(f"聊天模型: {settings.CHAT_MODEL}")
    logger.info(f"BI 模型: {settings.BI_MODEL}")
    logger.info(f"图片模型: {settings.IMAGE_MODEL}")
    logger.info("=" * 50)
    yield
    # 关闭时
    logger.info("AI 智能客服综合平台已关闭")


app = FastAPI(
    title="AI 智能客服综合平台",
    description="基于 LangChain + FastAPI 构建的智能客服、Text2SQL、BI 报表、AI 生图综合平台",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请替换为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router.router)
app.include_router(image_router.router)
app.include_router(question_router.router)
app.include_router(bi_router.router)


@app.get("/")
async def root():
    """根路径 - 服务健康检查"""
    return {
        "service": "AI 智能客服综合平台",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/ai/chat",
            "chat_stream": "/ai/stream",
            "chat_agent": "/ai/chat/agent",
            "chat_role": "/ai/chat/role",
            "text2sql": "/ai/text2sql",
            "history": "/ai/history",
            "charts": "/ai/charts",
            "image": "/ai/image",
            "grade": "/question/grade",
        },
    }


if __name__ == "__main__":
    import sys
    import uvicorn

    # 支持命令行参数覆盖端口: python -m app.main --port 8089
    port = settings.SERVER_PORT
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=port,
        reload=True,
    )