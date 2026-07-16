"""Pydantic 数据模型（请求/响应）"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ============================================
# 对话相关
# ============================================

class ChatRequest(BaseModel):
    """对话请求"""
    msg: str = Field(..., description="用户输入的消息")
    session_id: str = Field(default="1", description="会话ID")


class ChatMessage(BaseModel):
    """对话消息"""
    message_type: str = Field(..., alias="messageType", description="消息类型: USER/ASSISTANT")
    text: str = Field(..., description="消息内容")
    metadata: Optional[dict] = None


class ChatHistoryResponse(BaseModel):
    """对话历史响应"""
    session_id: str
    messages: list[ChatMessage]


# ============================================
# BI 图表相关
# ============================================

class ResultChart(BaseModel):
    """BI 图表返回数据"""
    title: str = Field(default="", description="图表标题")
    xAxis: list[str] = Field(default=[], description="X轴标签")
    series: list[float] = Field(default=[], description="数值数据")
    labels: list[str] = Field(default=[], description="图例标签")
    analysis: str = Field(default="", description="数据分析文本")


# ============================================
# AI 角色相关
# ============================================

class AIRole(BaseModel):
    """AI 角色定义"""
    role_name: str = Field(default="", description="角色名称")
    personality: str = Field(default="", description="性格特征")
    expertise: str = Field(default="", description="专业领域")
    communication_style: str = Field(default="", description="沟通风格")
    constraints: list[str] = Field(default=[], description="约束条件")


# ============================================
# AI 阅卷相关
# ============================================

class QuestionGradeRequest(BaseModel):
    """阅卷请求"""
    question_id: int = Field(..., description="题目ID")
    user_answer: str = Field(..., description="用户回答")


# ============================================
# 约课相关
# ============================================

class ReservationRequest(BaseModel):
    """约课请求"""
    student_name: str = Field(..., description="学生姓名")
    course_name: str = Field(..., description="课程名称")


# ============================================
# 通用
# ============================================

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    """成功响应"""
    message: str = Field(..., description="成功信息")
    data: Any = None