from typing import Any, Dict, List, Optional, Union
from query_builder import PyQueryBuilder
from tortoise import Tortoise
from tortoise.models import Model
import os
from pathlib import Path


class ComplexQueryBuilder:
    """基于 query-builder-tool 的复杂查询构建器"""
    
    def __init__(self, model: Optional[Model] = None, template_dir: Optional[str] = None):
        self.model = model
        self.table_name = model._meta.db_table if model else None
        
        # 设置模板目录
        if template_dir is None:
            template_dir = str(Path(__file__).parent.parent / "sql_templates")
        
        self.query_builder = PyQueryBuilder(template_dir=template_dir)
        
    def select(self, fields: Optional[List[str]] = None):
        """选择字段"""
        if fields:
            self.query_builder.select(fields)
        else:
            self.query_builder.select(["*"])
        return self
    
    def from_table(self, table: Optional[str] = None):
        """设置查询表"""
        table_name = table or self.table_name
        if table_name:
            self.query_builder.from_table(table_name)
        return self
    
    def where(self, field: str, operator: str, value: Any):
        """添加WHERE条件"""
        self.query_builder.where(field, operator, value)
        return self
    
    def where_in(self, field: str, values: List[Any]):
        """WHERE IN条件"""
        self.query_builder.where_in(field, values)
        return self
    
    def where_between(self, field: str, start: Any, end: Any):
        """WHERE BETWEEN条件"""
        self.query_builder.where_between(field, start, end)
        return self
    
    def where_like(self, field: str, pattern: str):
        """WHERE LIKE条件"""
        self.query_builder.where_like(field, f"%{pattern}%")
        return self
    
    def where_null(self, field: str, is_null: bool = True):
        """WHERE NULL条件"""
        if is_null:
            self.query_builder.where_null(field)
        else:
            self.query_builder.where_not_null(field)
        return self
    
    def or_where(self, field: str, operator: str, value: Any):
        """OR WHERE条件"""
        self.query_builder.or_where(field, operator, value)
        return self
    
    def join(self, table: str, on_condition: str, join_type: str = "INNER"):
        """添加JOIN"""
        if join_type.upper() == "LEFT":
            self.query_builder.left_join(table, on_condition)
        elif join_type.upper() == "RIGHT":
            self.query_builder.right_join(table, on_condition)
        else:
            self.query_builder.inner_join(table, on_condition)
        return self
    
    def left_join(self, table: str, on_condition: str):
        """LEFT JOIN"""
        self.query_builder.left_join(table, on_condition)
        return self
    
    def right_join(self, table: str, on_condition: str):
        """RIGHT JOIN"""
        self.query_builder.right_join(table, on_condition)
        return self
    
    def inner_join(self, table: str, on_condition: str):
        """INNER JOIN"""
        self.query_builder.inner_join(table, on_condition)
        return self
    
    def order_by(self, field: str, direction: str = "ASC"):
        """添加ORDER BY"""
        self.query_builder.order_by(field, direction)
        return self
    
    def group_by(self, *fields: str):
        """添加GROUP BY"""
        for field in fields:
            self.query_builder.group_by(field)
        return self
    
    def having(self, field: str, operator: str, value: Any):
        """添加HAVING"""
        self.query_builder.having(field, operator, value)
        return self
    
    def limit(self, count: int):
        """添加LIMIT"""
        self.query_builder.limit(count)
        return self
    
    def offset(self, count: int):
        """添加OFFSET"""
        self.query_builder.offset(count)
        return self
    
    def build(self) -> str:
        """构建SQL查询语句"""
        # 如果还没有设置表名，先设置
        if self.table_name and not hasattr(self.query_builder, '_table'):
            self.from_table()
        return self.query_builder.build()
    
    def build_with_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """使用模板构建复杂SQL查询"""
        return self.query_builder.build_with_template(template_name, context)
    
    async def execute(self) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        sql = self.build()
        connection = Tortoise.get_connection("default")
        result = await connection.execute_query(sql)
        return result[1]  # 返回查询结果，result[0]是列信息
    
    async def execute_template(self, template_name: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """使用模板执行复杂查询"""
        sql = self.build_with_template(template_name, context)
        connection = Tortoise.get_connection("default")
        result = await connection.execute_query(sql)
        return result[1]
    
    async def execute_raw(self, sql: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """执行原始SQL查询"""
        connection = Tortoise.get_connection("default")
        result = await connection.execute_query(sql, params or [])
        return result[1]


class UserQueryBuilder(ComplexQueryBuilder):
    """用户查询构建器"""
    
    def __init__(self):
        from app.models.models import User
        super().__init__(User)
    
    def active_users(self):
        """查询活跃用户"""
        return self.where("is_active", "=", True)
    
    def superusers(self):
        """查询超级用户"""
        return self.where("is_superuser", "=", True)
    
    def created_after(self, date: str):
        """查询指定日期后创建的用户"""
        return self.where("created_at", ">=", date)
    
    def with_email_domain(self, domain: str):
        """查询指定邮箱域名的用户"""
        return self.where_like("email", f"@{domain}")
    
    def with_profile(self):
        """关联用户资料表"""
        return self.left_join(
            "user_profiles", 
            "users.id = user_profiles.user_id"
        ).select([
            "users.*",
            "user_profiles.first_name",
            "user_profiles.last_name",
            "user_profiles.phone"
        ])
    
    def with_post_count(self):
        """查询用户及其文章数量"""
        return self.left_join(
            "posts",
            "users.id = posts.author_id"
        ).select([
            "users.id",
            "users.username", 
            "users.email",
            "COUNT(posts.id) as post_count"
        ]).group_by("users.id", "users.username", "users.email")
    
    def top_authors(self, limit: int = 10):
        """查询发文章最多的作者"""
        return self.with_post_count().having("post_count", ">", 0).order_by("post_count", "DESC").limit(limit)


class PostQueryBuilder(ComplexQueryBuilder):
    """文章查询构建器（示例）"""
    
    def __init__(self):
        # 注意：这里假设有Post模型，实际项目中根据需要调整
        super().__init__()
        self.table_name = "posts"  # 直接设置表名
    
    def published(self):
        """查询已发布文章"""
        return self.where("is_published", "=", True)
    
    def by_author(self, author_id: int):
        """查询指定作者的文章"""
        return self.where("author_id", "=", author_id)
    
    def by_title_keyword(self, keyword: str):
        """根据标题关键词查询"""
        return self.where_like("title", keyword)
    
    def recent_posts(self, days: int = 7):
        """查询最近几天的文章"""
        from datetime import datetime, timedelta
        date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
        return self.where("created_at", ">=", date_threshold)
    
    def with_author_info(self):
        """关联作者信息"""
        return self.inner_join(
            "users",
            "posts.author_id = users.id"
        ).select([
            "posts.*",
            "users.username as author_username",
            "users.email as author_email"
        ])
    
    def popular_posts(self, limit: int = 10):
        """热门文章"""
        return self.published().order_by("created_at", "DESC").limit(limit)


# 使用示例函数
async def query_examples():
    """查询示例"""
    
    # 1. 查询活跃用户
    active_users = await (
        UserQueryBuilder()
        .active_users()
        .order_by("created_at", "DESC")
        .limit(20)
        .execute()
    )
    
    # 2. 查询超级用户
    superusers = await (
        UserQueryBuilder()
        .superusers()
        .execute()
    )
    
    # 3. 查询gmail用户
    gmail_users = await (
        UserQueryBuilder()
        .with_email_domain("gmail.com")
        .execute()
    )
    
    # 4. 使用模板查询复杂统计信息
    template_context = {
        "date_from": "2024-01-01",
        "date_to": "2024-12-31",
        "limit": 10
    }
    
    complex_stats = await (
        ComplexQueryBuilder()
        .execute_template("user_stats", template_context)
    )
    
    return {
        "active_users": active_users,
        "superusers": superusers,
        "gmail_users": gmail_users,
        "complex_stats": complex_stats
    }


# SQL模板示例 - 需要在 app/sql_templates/ 目录下创建对应的 .sql 文件
def create_template_examples():
    """创建SQL模板示例"""
    templates = {
        "user_stats.sql": """
        SELECT 
            u.id,
            u.username,
            u.email,
            COUNT(up.id) as profile_count,
            u.created_at,
            CASE 
                WHEN u.is_active = true THEN '活跃'
                ELSE '非活跃'
            END as status
        FROM users u
        LEFT JOIN user_profiles up ON u.id = up.user_id
        WHERE u.created_at BETWEEN '{{ date_from }}' AND '{{ date_to }}'
        GROUP BY u.id, u.username, u.email, u.created_at, u.is_active
        ORDER BY profile_count DESC, u.created_at DESC
        LIMIT {{ limit }}
        """,
        
        "complex_join.sql": """
        SELECT 
            u.username,
            u.email,
            up.first_name,
            up.last_name,
            up.phone,
            COUNT(*) as total_records
        FROM users u
        INNER JOIN user_profiles up ON u.id = up.user_id
        WHERE u.is_active = true
        {% if email_domain %}
        AND u.email LIKE '%@{{ email_domain }}'
        {% endif %}
        GROUP BY u.id, u.username, u.email, up.first_name, up.last_name, up.phone
        HAVING COUNT(*) > {{ min_count | default(value=0) }}
        ORDER BY total_records DESC
        """
    }
    
    return templates