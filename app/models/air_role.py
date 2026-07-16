"""AI 角色定义模型"""

from dataclasses import dataclass, field


@dataclass
class AIRole:
    """AI 角色定义"""
    role_name: str = ""                          # 角色名称
    personality: str = ""                        # 性格特征
    expertise: str = ""                          # 专业领域
    communication_style: str = ""                # 沟通风格
    constraints: list[str] = field(default_factory=list)  # 约束条件