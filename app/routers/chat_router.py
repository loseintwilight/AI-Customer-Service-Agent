"""智能客服 & Text2SQL 路由 — 集成 RAG检索 + Tool Calling + 角色化聊天"""

import json
from typing import Optional

from fastapi import APIRouter, Query
from langchain_community.chat_models import ChatTongyi
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.services.chat_service import ChatService
from app.services.prompt_template_service import PromptTemplateService
from app.services.vector_store_service import VectorStoreService
from app.models.air_role import AIRole
from app.tools.chat_tools import add_reservation
from app.utils.redis_cache import RedisCache

router = APIRouter(prefix="/ai", tags=["智能客服"])

# 对话模型
chat_llm = ChatTongyi(
    model=settings.CHAT_MODEL,
    dashscope_api_key=settings.DASHSCOPE_API_KEY,
    temperature=0.7,
)

# 低温度模型（用于 SQL 生成等精确任务）
precise_llm = ChatTongyi(
    model=settings.CHAT_MODEL,
    dashscope_api_key=settings.DASHSCOPE_API_KEY,
    temperature=0.1,
)

# 服务实例
chat_service = ChatService()
prompt_template_service = PromptTemplateService()

# Tool Calling 工具列表
TOOLS = [add_reservation]


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    """获取会话历史"""
    return RedisChatMessageHistory(
        session_id=session_id,
        url=settings.REDIS_URL,
        key_prefix="spring_ai_alibaba_chat_memory:",
    )


def _build_system_prompt(
    role: Optional[AIRole] = None,
    enable_rag: bool = True,
    user_query: str = "",
) -> str:
    """
    构建系统提示词，集成了：
    - 角色定义（对应 Java 文档 §2.6 预设角色 + §3.2 角色调优）
    - RAG 知识库检索（对应 Java 文档 §2.5 向量存储）

    Args:
        role: AI 角色定义（可选）
        enable_rag: 是否启用 RAG 检索
        user_query: 用户查询（用于 RAG 检索）

    Returns:
        完整的系统提示词
    """
    parts = []

    # 1. 角色定义（对应 AIRole + CustomerServicePromptTemplate）
    if role is not None:
        role_prompt = prompt_template_service.build_role_specific_prompt(
            role, ""
        )
        # 移除末尾的 "用户输入：" 部分，只保留角色定义
        role_prompt = role_prompt.replace("\n用户输入：\n\n请严格按照角色定义回答：", "")
        parts.append(role_prompt)
    else:
        parts.append("您是小刘，是一个智能客服助手，态度良好，请友好地回答用户的问题。")

    # 2. RAG 知识库上下文（对应 QuestionAnswerAdvisor）
    if enable_rag and user_query:
        retrieved_docs = VectorStoreService.retrieve(user_query, top_k=2)
        if retrieved_docs:
            parts.append("\n【参考知识库内容】")
            for i, doc in enumerate(retrieved_docs, 1):
                parts.append(f"{i}. {doc}")
            parts.append("请参考以上知识库内容回答用户问题，如果知识库内容与问题无关，请忽略。")

    return "\n".join(parts)


def _create_default_role() -> AIRole:
    """创建默认 AI 角色（对应 Java 文档 createDefaultRole）"""
    return AIRole(
        role_name="小刘",
        personality="热情友好，耐心细致",
        expertise="智能客服和知识问答",
        communication_style="亲切自然，专业可靠",
        constraints=[
            "保持友好、专业的态度",
            "如果不知道答案，诚实告知",
            "回答简洁明了，重点突出",
        ],
    )


# ============================================================
# 端点一：普通对话（支持 RAG + 角色化）
# 对应 Java 文档 02 §3.2 & 02 §2.5
# ============================================================

@router.get("/chat")
async def chat(
    msg: str = Query(..., description="用户输入的消息"),
    session_id: str = Query(default="1", description="会话ID"),
    role_name: Optional[str] = Query(
        default=None, description="可选的角色名称，如：客服助手、明星介绍助手"
    ),
):
    """
    智能客服对话接口（普通输出）

    - 支持多轮对话记忆（Redis）
    - 支持 RAG 向量检索（自动从 ChromaDB 检索相关知识）
    - 支持角色化聊天（可选 role_name 参数）
    """
    role = _create_default_role()
    if role_name:
        role.role_name = role_name
        role.expertise = f"{role_name}相关领域"

    system_prompt = _build_system_prompt(role=role, enable_rag=True, user_query=msg)

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


# ============================================================
# 端点二：流式对话（支持 RAG + 角色化）
# 对应 Java 文档 02 §1.3 流式输出
# ============================================================

@router.get("/stream")
async def chat_stream(
    msg: str = Query(..., description="用户输入的消息"),
    session_id: str = Query(default="1", description="会话ID"),
):
    """
    流式输出对话接口（SSE 模式）

    - 支持多轮对话记忆
    - 支持 RAG 向量检索
    - SSE 实时推送
    """
    role = _create_default_role()
    system_prompt = _build_system_prompt(role=role, enable_rag=True, user_query=msg)

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


# ============================================================
# 端点三：Agent 工具调用聊天（支持 Tool Calling）
# 对应 Java 文档 04 §2.2-2.3 Tool工具方法 + defaultTools
# ============================================================

@router.get("/chat/agent")
async def chat_agent(
    msg: str = Query(..., description="用户输入的消息，如：帮小明预约数学课"),
    session_id: str = Query(default="1", description="会话ID"),
):
    """
    Agent 工具调用聊天接口

    集成了 Tool Calling 能力，大模型可以自动调用工具完成操作：
    - 约课操作：当用户说"帮xx预约xx课"时，自动调用 add_reservation 工具
    - 支持 RAG 知识库检索

    对应 Java 文档：
    - 04 §2.2 ChatTools + @Tool 注解
    - 04 §2.3 AIConfig.defaultTools(chatTools)
    """
    role = _create_default_role()
    role.expertise = "约课助手和智能客服"
    system_prompt = _build_system_prompt(role=role, enable_rag=True, user_query=msg)
    system_prompt += (
        "\n\n你可以使用工具来帮助学生预约课程。"
        "当用户表达约课/选课/预约意图时，请调用 add_reservation 工具。"
        "调用工具前请确认已获取学生姓名和课程名称。"
    )

    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(chat_llm, TOOLS, agent_prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )

    agent_with_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    response = agent_with_history.invoke(
        {"input": msg},
        config={"configurable": {"session_id": session_id}},
    )

    return {"response": response["output"]}


# ============================================================
# 端点四：角色化聊天（使用 AIRole 结构化角色）
# 对应 Java 文档 03 §2.1-2.4 角色调优
# ============================================================

@router.get("/chat/role")
async def chat_with_role(
    msg: str = Query(..., description="用户输入的消息"),
    session_id: str = Query(default="1", description="会话ID"),
    role_name: str = Query(default="小刘", description="角色名称"),
    personality: str = Query(default="热情友好，耐心细致", description="性格特征"),
    expertise: str = Query(default="智能客服", description="专业领域"),
    communication_style: str = Query(
        default="亲切自然，专业可靠", description="沟通风格"
    ),
):
    """
    角色化聊天接口

    使用结构化的 AIRole 定义角色，通过 PromptTemplateService 生成角色化提示词。
    支持 RAG 知识库检索。

    对应 Java 文档：
    - 03 §2.1 AIRole 实体类
    - 03 §2.2 CustomerServicePromptTemplate
    - 03 §2.3 PromptTemplateService
    - 03 §2.4 createDefaultRole + chat 方法
    """
    role = AIRole(
        role_name=role_name,
        personality=personality,
        expertise=expertise,
        communication_style=communication_style,
        constraints=[
            "保持友好、专业的态度",
            "严格遵循角色设定回答",
            "如果不知道答案，诚实告知",
        ],
    )

    system_prompt = _build_system_prompt(role=role, enable_rag=True, user_query=msg)

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


# ============================================================
# 端点五：Text2SQL
# 对应 Java 文档 04 §1.3 ChatServiceImpl
# ============================================================

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


# ============================================================
# 端点六：对话历史管理
# 对应 Java 文档 02 §3.4 对话历史
# ============================================================

@router.get("/history")
async def get_chat_history(
    session_id: str = Query(default="1", description="会话ID"),
):
    """获取对话历史"""
    history = get_session_history(session_id)
    messages = []
    for m in history.messages:
        messages.append({
            "messageType": "USER" if m.type == "human" else "ASSISTANT",
            "text": m.content,
        })
    return {"session_id": session_id, "messages": messages}


@router.delete("/history")
async def delete_chat_history(
    session_id: str = Query(default="1", description="会话ID"),
):
    """删除对话历史"""
    await RedisCache.delete_chat_history(session_id)
    return {"message": "删除成功", "session_id": session_id}