"""BI 数据治理报表路由"""

from fastapi import APIRouter, Query

from app.services.chat_service import ChatService
from app.services.bi_service import BIService

router = APIRouter(prefix="/ai", tags=["BI 报表"])

# Text2SQL 服务
chat_service = ChatService()

# BI 分析服务
bi_service = BIService()


@router.get("/charts")
async def get_charts(
    text: str = Query(..., description="自然语言查询，如：查询各部门新增总和"),
):
    """
    BI 图表接口

    输入自然语言查询，流程：
    1. Text2SQL 将自然语言转为 SQL 并查询数据库
    2. 大模型分析查询结果，生成图表数据（标题、X轴标签、数值、分析文本）
    3. 返回结构化的图表数据供前端 ECharts 渲染

    支持生成条形图、折线图、饼图

    查询用例：
    - 查询薪资前5的教师
    - 统计学生的绩点分布
    - 根据入职年份查询教师薪资走向
    - 查询男学生、女学生各所占比例
    """
    # 1. Text2SQL 获取数据
    query_result = chat_service.get_chat_sql(text)

    # 2. 如果查询出错，返回错误
    if isinstance(query_result, dict) and "error" in query_result:
        return {
            "title": "数据错误",
            "xAxis": [],
            "series": [],
            "labels": [],
            "analysis": f"查询出错：{query_result['error']}",
        }

    # 3. 大模型分析生成图表
    chart_data = bi_service.get_charts_and_info(query_result)

    # 4. 转换为前端需要的格式
    return {
        "title": chart_data.title,
        "xAxis": chart_data.xAxis,
        "series": chart_data.series,
        "labels": chart_data.labels,
        "analysis": chart_data.analysis,
    }