"""对话消息模型"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChatMessage:
    """对话消息"""
    message_type: str = ""          # 消息类型: USER / ASSISTANT
    text: str = ""                  # 消息内容
    metadata: Optional[dict] = None  # 元数据