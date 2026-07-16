"""约课服务"""

from datetime import datetime

from app.models.database import SessionLocal, Student, Course, Reservation


class ReservationService:
    """约课业务服务"""

    @staticmethod
    def add_reservation(student_name: str, course_name: str) -> str:
        """
        根据学生姓名和课程名称预约课程

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
                return f"学生 [{student_name}] 不存在"
            if not course:
                return f"课程 [{course_name}] 不存在"

            # 创建预约
            reservation = Reservation(
                student_id=student.student_id,
                course_id=course.course_id,
                reservation_time=datetime.now(),
                status="已预约"
            )
            session.add(reservation)
            session.commit()

            return f"预约成功，学生 {student_name} 已预约课程 {course_name}"

        except Exception as e:
            session.rollback()
            return f"预约失败：{str(e)}"
        finally:
            session.close()