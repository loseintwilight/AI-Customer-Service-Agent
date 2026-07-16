"""AI 阅卷路由"""

from fastapi import APIRouter, Query
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.models.database import SessionLocal, Question

router = APIRouter(prefix="/question", tags=["AI 阅卷"])

# 阅卷模型
grading_llm = ChatTongyi(
    model=settings.CHAT_MODEL,
    dashscope_api_key=settings.DASHSCOPE_API_KEY,
    temperature=0.3,
)


@router.get("/grade")
async def grade_question(
    question_id: int = Query(..., description="题目ID"),
    user_answer: str = Query(..., description="用户回答"),
):
    """
    AI 阅卷接口

    根据题目 ID 从数据库获取标准答案和分值，
    结合用户回答由大模型进行评分和评语生成

    示例：
    /question/grade?question_id=1&user_answer=beforeDestroy和destroyed
    """
    session = SessionLocal()
    try:
        question = session.query(Question).filter(Question.id == question_id).first()
        if not question:
            return {"error": f"题目不存在: question_id={question_id}"}

        prompt_template = PromptTemplate.from_template("""
您是一个阅卷老师，请根据用户的回答，以及标准答案和分值，生成用户回答这个问题中相应的分数，并给出评判标准。

用户回答：
{user_answer}

标准答案：
{answer}

分值：
{score}
""")

        messages = [
            SystemMessage(content="你是一个专业的阅卷老师，评分公正，评判标准清晰。"),
            HumanMessage(content=prompt_template.format(
                user_answer=user_answer,
                answer=question.answer,
                score=question.score,
            ))
        ]

        response = grading_llm.invoke(messages)
        return {
            "question_id": question_id,
            "question": question.question,
            "score": question.score,
            "user_answer": user_answer,
            "standard_answer": question.answer,
            "grading_result": response.content,
        }

    finally:
        session.close()