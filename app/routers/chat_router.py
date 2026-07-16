"""智能客服 & Text2SQL 路由"""

import json
from typing import Optional

from fastapi import APIRouter, Query
from langchain_community.chat_models import ChatTongyi
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.services.chat_service import ChatService
from app.services.prompt_template_service import PromptTemplateService
from app.models.air_role import AIRole
from app.utils.redis_cache import RedisCache

router = APIRouter(prefix="/ai", tags=["智能客服"])

# 对话模型
chat_llm = ChatTongyi(
    model=settings.CHAT_MODEL,
    dashscope_api_key=settings.DASHSCOPE_API_KEY,
    temperature=0.7,
)

# Text2SQL 服务
chat_service = ChatService()

# 提示词模板服务
prompt_template_service = PromptTemplateService()


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    """获取会话历史"""
    return RedisChatMessageHistory(
        session_id=session_id,
        url=settings.REDIS_URL,
        key_prefix="spring_ai_alibaba_chat_memory:",
    )


@router.get("/chat")
async def chat(
    msg: str = Query(..., description="用户输入的消息"),
    session_id: str = Query(default="1", description="会话ID"),
):
    """
    智能客服对话接口

    - 支持多轮对话记忆
    - 支持预设角色
    - 普通输出模式
    """
    system_prompt = "您是小刘，是一个智能客服助手，态度良好，请友好地回答用户的问题。"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    chain = LLMChain(llm=chat_llm, prompt=prompt)

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    response = chain_with_history.invoke(
        {"input": msg},
        config={"configurable": {"session_id": session_id}},
    )

    return {"response": response["text"]}


@router.get("/stream")
async def chat_stream(
    msg: str = Query(..., description="用户输入的消息"),
    session_id: str = Query(default="1", description="会话ID"),
):
    """
    流式输出对话接口（SSE 模式）
    """
    system_prompt = "您是小刘，是一个智能客服助手，态度良好，请友好地回答用户的问题。"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    chain = LLMChain(llm=chat_llm, prompt=prompt)

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    async def event_generator():
        async for chunk in chain_with_history.astream_events(
            {"input": msg},
            config={"configurable": {"session_id": session_id}},
            version="v1",
        ):
            if chunk["event"] == "on_llm_new_token":
                yield {"event": "message", "data": chunk["data"]["chunk"]}

    return EventSourceResponse(event_generator())


@router.get("/text2sql")
async def text2sql(
    msg: str = Query(..., description="自然语言查询"),
):
    """
    Text2SQL 接口：将自然语言转换为 SQL 并执行

    示例：
    - 查询所有学生
    - 查询张三教的所有课程
    - 统计所有课程数量
    """
    result = chat_service.get_chat_sql(msg)
    return {"result": result}


@router.get("/history")
async def get_chat_history(
    session_id: str = Query(default="1", description="会话ID"),
):
    """获取对话历史"""
    history = get_session_history(session_id)
    messages = []
    for msg in history.messages:
        messages.append({
            "messageType": "USER" if msg.type == "human" else "ASSISTANT",
            "text": msg.content,
        })
    return {"session_id": session_id, "messages": messages}


@router.delete("/history")
async def delete_chat_history(
    session_id: str = Query(default="1", description="会话ID"),
):
    """删除对话历史"""
    await RedisCache.delete_chat_history(session_id)
    return {"message": "删除成功", "session_id": session_id}