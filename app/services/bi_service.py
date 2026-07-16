"""BI 图表分析服务：基于大模型生成图表数据和分析文本"""

import json
import re
from typing import Any

from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.models.schemas import ResultChart


class BIService:
    """BI 图表分析服务"""

    def __init__(self):
        self.llm = ChatTongyi(
            model=settings.BI_MODEL,
            dashscope_api_key=settings.DASHSCOPE_API_KEY,
            temperature=0.2,
        )

    def get_charts_and_info(self, query_result: Any) -> ResultChart:
        """
        根据数据库查询结果，生成图表数据和分析文本

        Args:
            query_result: 数据库查询结果

        Returns:
            ResultChart 对象
        """
        if not isinstance(query_result, list):
            return self._create_error_result("查询结果格式不正确")

        if not query_result:
            return self._create_error_result("查询结果为空")

        # 将查询结果转换为 JSON 字符串
        query_result_json = json.dumps(query_result, ensure_ascii=False, default=str)
        return self._generate_chart_from_data(query_result_json)

    def _generate_chart_from_data(self, query_result_json: str) -> ResultChart:
        """
        使用大模型生成图表数据和分析

        Args:
            query_result_json: 查询结果 JSON 字符串

        Returns:
            ResultChart 对象
        """
        prompt_template = PromptTemplate.from_template("""
根据以下数据库查询结果，生成适合图表展示的数据格式和分析文本：

查询结果：{query_result}

请按照以下要求生成结果：
1. 分析数据内容，提取合适的标题
2. 选择合适的列作为x轴标签（通常是分类列）
3. 选择合适的列作为y轴数据（通常是数值列）
4. 生成数据分析文本，包括：
   - 数据概览
   - 最大值、最小值及其对应的标签
   - 平均值、总和
   - 趋势分析（如果适用）
5. 返回严格符合以下JSON格式的结果：
{{"title": "图表标题", "xAxis": ["标签1", "标签2", "标签3"], "series": [数值1, 数值2, 数值3], "labels": ["标签1", "标签2", "标签3"], "analysis": "数据分析文本"}}
""")

        messages = [
            SystemMessage(content="你是一个数据分析专家，负责将数据库查询结果转换为图表展示数据。"),
            HumanMessage(content=prompt_template.format(query_result=query_result_json))
        ]

        response = self.llm.invoke(messages)
        ai_response = response.content.strip()

        # 清理 JSON 字符串
        ai_response = re.sub(r"```json\s*|```\s*", "", ai_response).strip()

        try:
            result_dict = json.loads(ai_response)
            result_chart = ResultChart(
                title=result_dict.get("title", ""),
                xAxis=result_dict.get("xAxis", result_dict.get("x_axis", [])),
                series=result_dict.get("series", []),
                labels=result_dict.get("labels", []),
                analysis=result_dict.get("analysis", ""),
            )
            return result_chart
        except json.JSONDecodeError as e:
            return self._create_error_result(f"解析 AI 响应出错: {str(e)}")

    @staticmethod
    def _create_error_result(error_message: str) -> ResultChart:
        """创建错误结果"""
        return ResultChart(
            title="数据错误",
            analysis=error_message
        )