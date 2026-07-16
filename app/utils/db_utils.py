"""数据库表结构反射工具，用于 Text2SQL 时获取表结构和关系信息"""

from typing import Any
from sqlalchemy import inspect, MetaData, Table, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.database import engine, Student, Teacher, Course, Reservation


def get_table_info(table_names: list[str]) -> str:
    """
    获取指定表的结构信息，用于注入到提示词模板中

    Args:
        table_names: 表名列表

    Returns:
        格式化的表结构描述字符串
    """
    inspector = inspect(engine)
    table_info_parts = []

    for table_name in table_names:
        table_info_parts.append(f"表名：{table_name}")
        table_info_parts.append("表结构：")

        columns = inspector.get_columns(table_name)
        for col in columns:
            col_name = col["name"]
            col_type = str(col["type"])
            pk_cols = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
            is_pk = "是" if col_name in pk_cols else "否"
            nullable = "是" if col.get("nullable", True) else "否"
            comment = col.get("comment", "")
            table_info_parts.append(
                f"  - {col_name} ({col_type}) 主键:{is_pk} 可空:{nullable} 注释:{comment}"
            )
        table_info_parts.append("")

    # 添加表关系信息
    table_info_parts.append("表间关系：")
    table_names_lower = [t.lower() for t in table_names]

    if "teacher" in table_names_lower and "course" in table_names_lower:
        table_info_parts.append("  - teacher.teacher_id 关联 course.teacher_id")

    if "student" in table_names_lower and "reservation" in table_names_lower:
        table_info_parts.append("  - student.student_id 关联 reservation.student_id")

    if "course" in table_names_lower and "reservation" in table_names_lower:
        table_info_parts.append("  - course.course_id 关联 reservation.course_id")

    return "\n".join(table_info_parts)


def get_all_table_names() -> list[str]:
    """获取数据库中所有表名"""
    inspector = inspect(engine)
    return inspector.get_table_names()


def execute_sql_query(sql: str) -> list[dict[str, Any]]:
    """
    执行 SQL 查询并返回结果

    Args:
        sql: SQL 查询语句

    Returns:
        查询结果列表
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = result.keys()
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]


def execute_sql_update(sql: str) -> int:
    """
    执行 SQL 更新操作

    Args:
        sql: SQL 更新语句

    Returns:
        影响行数
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        conn.commit()
        return result.rowcount