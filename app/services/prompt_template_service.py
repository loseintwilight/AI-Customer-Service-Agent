"""提示词模板服务"""

from app.models.air_role import AIRole


class PromptTemplateService:
    """提示词模板服务"""

    @staticmethod
    def build_role_specific_prompt(role: AIRole, user_input: str) -> str:
        """
        构建角色特定的提示词模板

        Args:
            role: AI 角色定义
            user_input: 用户输入

        Returns:
            格式化的提示词
        """
        constraints_text = "\n".join(f"- {c}" for c in role.constraints)
        return f"""
角色定义：
名称：{role.role_name}
性格：{role.personality}
专业领域：{role.expertise}
沟通风格：{role.communication_style}

约束条件：
{constraints_text}

用户输入：{user_input}

请严格按照角色定义回答：
""".strip()

    @staticmethod
    def build_basic_prompt(user_input: str) -> str:
        """
        构建基础提示词模板（无角色）

        Args:
            user_input: 用户输入

        Returns:
            格式化的提示词
        """
        return f"""
用户输入：{user_input}

请根据上下文回答用户问题：
""".strip()

    @staticmethod
    def build_prompt_with_examples(role: AIRole, user_input: str, examples: str) -> str:
        """
        构建带示例的提示词模板

        Args:
            role: AI 角色定义
            user_input: 用户输入
            examples: 示例对话

        Returns:
            格式化的提示词
        """
        constraints_text = "\n".join(f"- {c}" for c in role.constraints)
        return f"""
角色定义：
名称：{role.role_name}
性格：{role.personality}
专业领域：{role.expertise}
沟通风格：{role.communication_style}

约束条件：
{constraints_text}

对话示例：
{examples}

用户输入：{user_input}

请参考角色定义和对话示例，严格按角色要求回答：
""".strip()

    @staticmethod
    def generate_prompt(role: AIRole | None, user_input: str) -> str:
        """
        根据角色生成提示词

        Args:
            role: AI 角色（可为空）
            user_input: 用户输入

        Returns:
            完整提示词
        """
        if role is not None:
            return PromptTemplateService.build_role_specific_prompt(role, user_input)
        return PromptTemplateService.build_basic_prompt(user_input)

    @staticmethod
    def generate_prompt_with_examples(role: AIRole, user_input: str, examples: str) -> str:
        """
        生成带示例的提示词

        Args:
            role: AI 角色
            user_input: 用户输入
            examples: 对话示例

        Returns:
            完整提示词
        """
        return PromptTemplateService.build_prompt_with_examples(role, user_input, examples)