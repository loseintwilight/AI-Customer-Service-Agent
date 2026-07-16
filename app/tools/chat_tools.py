"""LangChain 工具函数定义（Tool Calling）"""

from langchain_core.tools import tool

from app.models.database import SessionLocal, Student, Course, Reservation
from datetime import datetime


@tool(description="根据学生姓名和课程名称进行预约选课")
def add_reservation(student_name: str, course_name: str) -> str:
    """
    根据学生姓名和课程名称进行预约选课

    Args:
        student_name: 学生姓名
        course_name: 课程名称

    Returns:
        预约结果信息
    """
    session = SessionLocal()
    try:
        # 查找学生
        student = session.query(Student).filter(
            Student.student_name == student_name
        ).first()

        # 查找课程
        course = session.query(Course).filter(
            Course.course_name == course_name
        ).first()

        if not student:
            return f"找不到学生：{student_name}"
        if not course:
            return f"找不到课程：{course_name}"

        # 创建预约
        reservation = Reservation(
            student_id=student.student_id,
            course_id=course.course_id,
            reservation_time=datetime.now(),
            status="已预约"
        )
        session.add(reservation)
        session.commit()

        return f"预约成功！学生 {student_name} 已成功预约课程 {course_name}"

    except Exception as e:
        session.rollback()
        return f"预约失败：{str(e)}"
    finally:
        session.close()