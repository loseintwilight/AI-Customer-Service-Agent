"""Text2SQL 服务：将自然语言转换为 SQL 并执行"""

import re
from typing import Any

from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.utils.db_utils import get_table_info, execute_sql_query, execute_sql_update


class ChatService:
    """Text2SQL 服务"""

    def __init__(self):
        self.llm = ChatTongyi(
            model=settings.CHAT_MODEL,
            dashscope_api_key=settings.DASHSCOPE_API_KEY,
            temperature=0.1,
        )

    def get_chat_sql(self, msg: str) -> Any:
        """
        将自然语言转换为 SQL 并执行

        Args:
            msg: 自然语言查询

        Returns:
            查询结果或错误信息
        """
        generated_sql = self._get_sql_by_text(msg)
        if not generated_sql:
            return {"error": "无法生成 SQL 语句"}

        try:
            return self._execute_sql(generated_sql)
        except Exception as e:
            return {"error": f"执行 SQL 时出错: {str(e)}"}

    def _get_sql_by_text(self, text: str) -> str:
        """
        通过自然语言生成 SQL

        Args:
            text: 自然语言文本

        Returns:
            生成的 SQL 语句
        """
        # 获取表结构信息
        table_names = ["student", "teacher", "course", "reservation"]
        table_info = get_table_info(table_names)

        prompt_template = PromptTemplate.from_template("""
将以下自然语言转换为 SQL 语句：{text}
请确保 SQL 语法正确，并适用于 MySQL 数据库。

{table_info}

请根据这些表和字段生成合适的 SQL 语句：
1. 如果是查询操作，生成 SELECT 语句。
2. 如果是新增操作，生成 INSERT 语句。
3. 如果是修改操作，生成 UPDATE 语句。
4. 如果是删除操作，生成 DELETE 语句。
5. 如果涉及多表查询，请使用适当的 JOIN 语句。
6. 注意表之间的关联关系，确保 JOIN 条件正确。
7. 查询条件和结果相关字段必须存在。
8. 生成的结果只有 sql，不要包含其他内容，不要包含代码块标记。
""")

        messages = [
            SystemMessage(content="你是一个专业的 SQL 生成助手，负责将自然语言转换为合法的 MySQL SQL 语句。"),
            HumanMessage(content=prompt_template.format(text=text, table_info=table_info))
        ]

        response = self.llm.invoke(messages)
        generated_sql = response.content.strip()

        # 清理 SQL 语句
        generated_sql = re.sub(r"(?i)^\s*sql\s*", "", generated_sql).strip()
        # 移除代码块标记
        generated_sql = re.sub(r"```sql\s*|```\s*", "", generated_sql).strip()

        return generated_sql

    def _execute_sql(self, sql: str) -> Any:
        """
        判断 SQL 类型并执行

        Args:
            sql: SQL 语句

        Returns:
            执行结果
        """
        upper_sql = sql.strip().upper()

        if upper_sql.startswith("SELECT"):
            result = execute_sql_query(sql)
            return result
        elif any(upper_sql.startswith(kw) for kw in ("INSERT", "UPDATE", "DELETE")):
            rows_affected = execute_sql_update(sql)
            return {"message": f"操作成功，影响行数: {rows_affected}"}
        else:
            return {"error": f"不支持的 SQL 类型: {sql}"}