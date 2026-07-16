"""SQLAlchemy 数据库模型定义"""

from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Date, DateTime,
    DECIMAL, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from app.config import settings

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL, pool_size=10, max_overflow=20)

# 声明基类
Base = declarative_base()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Student(Base):
    """学生表"""
    __tablename__ = "student"

    student_id = Column(Integer, primary_key=True, autoincrement=True, comment="学生ID")
    student_name = Column(String(50), nullable=False, comment="学生姓名")
    gender = Column(String(10), nullable=True, comment="性别")
    email = Column(String(100), nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    grade = Column(DECIMAL(5, 2), nullable=True, comment="绩点")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    reservations = relationship("Reservation", back_populates="student")


class Teacher(Base):
    """教师表"""
    __tablename__ = "teacher"

    teacher_id = Column(Integer, primary_key=True, autoincrement=True, comment="教师ID")
    teacher_name = Column(String(50), nullable=False, comment="教师姓名")
    gender = Column(String(10), nullable=True, comment="性别")
    phone = Column(String(20), nullable=True, comment="手机号")
    email = Column(String(100), nullable=True, comment="邮箱")
    salary = Column(DECIMAL(10, 2), nullable=True, comment="薪资")
    hire_date = Column(Date, nullable=True, comment="入职日期")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    courses = relationship("Course", back_populates="teacher")


class Course(Base):
    """课程表"""
    __tablename__ = "course"

    course_id = Column(Integer, primary_key=True, autoincrement=True, comment="课程ID")
    course_name = Column(String(100), nullable=False, comment="课程名称")
    teacher_id = Column(Integer, ForeignKey("teacher.teacher_id"), nullable=True, comment="授课教师ID")
    capacity = Column(Integer, default=0, comment="课程容量")
    total_hours = Column(Integer, default=0, comment="总课时")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    teacher = relationship("Teacher", back_populates="courses")
    reservations = relationship("Reservation", back_populates="course")

    __table_args__ = (
        Index("idx_teacher_id", "teacher_id"),
    )


class Reservation(Base):
    """预约表"""
    __tablename__ = "reservation"

    reservation_id = Column(Integer, primary_key=True, autoincrement=True, comment="预约ID")
    student_id = Column(Integer, ForeignKey("student.student_id"), nullable=False, comment="学生ID")
    course_id = Column(Integer, ForeignKey("course.course_id"), nullable=False, comment="课程ID")
    reservation_time = Column(DateTime, default=datetime.now, comment="预约时间")
    status = Column(String(20), default="已预约", comment="预约状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    student = relationship("Student", back_populates="reservations")
    course = relationship("Course", back_populates="reservations")

    __table_args__ = (
        Index("idx_student_id", "student_id"),
        Index("idx_course_id", "course_id"),
    )


class Question(Base):
    """题目表（用于 AI 阅卷）"""
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="题目ID")
    question = Column(Text, nullable=False, comment="题目内容")
    answer = Column(Text, nullable=False, comment="标准答案")
    score = Column(Integer, default=0, comment="分值")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")