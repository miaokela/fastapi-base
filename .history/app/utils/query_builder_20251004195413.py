from typing import Any, Dict, List, Optional, Union
from query_builder_tool import QueryBuilder, Condition, OrderBy, Join
from tortoise import Tortoise
from tortoise.models import Model


class ComplexQueryBuilder:
    """复杂SQL查询构建器"""
    
    def __init__(self, model: Model):
        self.model = model
        self.query_builder = QueryBuilder()
        self.table_name = model._meta.db_table
        
    def select(self, fields: Optional[List[str]] = None) -> 'ComplexQueryBuilder':
        """选择字段"""
        if fields:
            self.query_builder.select(*fields)
        else:
            self.query_builder.select("*")
        return self
    
    def from_table(self, table: Optional[str] = None) -> 'ComplexQueryBuilder':
        """设置查询表"""
        table_name = table or self.table_name
        self.query_builder.from_table(table_name)
        return self
    
    def where(self, field: str, operator: str, value: Any) -> 'ComplexQueryBuilder':
        """添加WHERE条件"""
        condition = Condition(field, operator, value)
        self.query_builder.where(condition)
        return self
    
    def where_in(self, field: str, values: List[Any]) -> 'ComplexQueryBuilder':
        """WHERE IN条件"""
        condition = Condition(field, "IN", values)
        self.query_builder.where(condition)
        return self
    
    def where_between(self, field: str, start: Any, end: Any) -> 'ComplexQueryBuilder':
        """WHERE BETWEEN条件"""
        start_condition = Condition(field, ">=", start)
        end_condition = Condition(field, "<=", end)
        self.query_builder.where(start_condition).where(end_condition)
        return self
    
    def where_like(self, field: str, pattern: str) -> 'ComplexQueryBuilder':
        """WHERE LIKE条件"""
        condition = Condition(field, "LIKE", f"%{pattern}%")
        self.query_builder.where(condition)
        return self
    
    def where_null(self, field: str, is_null: bool = True) -> 'ComplexQueryBuilder':
        """WHERE NULL条件"""
        operator = "IS NULL" if is_null else "IS NOT NULL"
        condition = Condition(field, operator, None)
        self.query_builder.where(condition)
        return self
    
    def or_where(self, field: str, operator: str, value: Any) -> 'ComplexQueryBuilder':
        """OR WHERE条件"""
        condition = Condition(field, operator, value)
        self.query_builder.or_where(condition)
        return self
    
    def join(self, table: str, on_condition: str, join_type: str = "INNER") -> 'ComplexQueryBuilder':
        """添加JOIN"""
        join = Join(table, on_condition, join_type)
        self.query_builder.join(join)
        return self
    
    def left_join(self, table: str, on_condition: str) -> 'ComplexQueryBuilder':
        """LEFT JOIN"""
        return self.join(table, on_condition, "LEFT")
    
    def right_join(self, table: str, on_condition: str) -> 'ComplexQueryBuilder':
        """RIGHT JOIN"""
        return self.join(table, on_condition, "RIGHT")
    
    def inner_join(self, table: str, on_condition: str) -> 'ComplexQueryBuilder':
        """INNER JOIN"""
        return self.join(table, on_condition, "INNER")
    
    def order_by(self, field: str, direction: str = "ASC") -> 'ComplexQueryBuilder':
        """添加ORDER BY"""
        order = OrderBy(field, direction)
        self.query_builder.order_by(order)
        return self
    
    def group_by(self, *fields: str) -> 'ComplexQueryBuilder':
        """添加GROUP BY"""
        self.query_builder.group_by(*fields)
        return self
    
    def having(self, condition: str) -> 'ComplexQueryBuilder':
        """添加HAVING"""
        self.query_builder.having(condition)
        return self
    
    def limit(self, count: int) -> 'ComplexQueryBuilder':
        """添加LIMIT"""
        self.query_builder.limit(count)
        return self
    
    def offset(self, count: int) -> 'ComplexQueryBuilder':
        """添加OFFSET"""
        self.query_builder.offset(count)
        return self
    
    def build(self) -> str:
        """构建SQL查询语句"""
        return self.query_builder.build()
    
    async def execute(self) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        sql = self.build()
        connection = Tortoise.get_connection("default")
        result = await connection.execute_query(sql)
        return result[1]  # 返回查询结果，result[0]是列信息
    
    async def execute_raw(self, sql: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """执行原始SQL查询"""
        connection = Tortoise.get_connection("default")
        result = await connection.execute_query(sql, params or [])
        return result[1]


class UserQueryBuilder(ComplexQueryBuilder):
    """用户查询构建器示例"""
    
    def __init__(self):
        from app.models.models import User
        super().__init__(User)
    
    def active_users(self) -> 'UserQueryBuilder':
        """查询活跃用户"""
        return self.where("is_active", "=", True)
    
    def superusers(self) -> 'UserQueryBuilder':
        """查询超级用户"""
        return self.where("is_superuser", "=", True)
    
    def created_after(self, date: str) -> 'UserQueryBuilder':
        """查询指定日期后创建的用户"""
        return self.where("created_at", ">=", date)
    
    def with_email_domain(self, domain: str) -> 'UserQueryBuilder':
        """查询指定邮箱域名的用户"""
        return self.where("email", "LIKE", f"%@{domain}")
    
    def with_profile(self) -> 'UserQueryBuilder':
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
    
    def with_post_count(self) -> 'UserQueryBuilder':
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
    
    def top_authors(self, limit: int = 10) -> 'UserQueryBuilder':
        """查询发文章最多的作者"""
        return self.with_post_count().having("COUNT(posts.id) > 0").order_by("post_count", "DESC").limit(limit)


class PostQueryBuilder(ComplexQueryBuilder):
    """文章查询构建器示例"""
    
    def __init__(self):
        from app.models.models import Post
        super().__init__(Post)
    
    def published(self) -> 'PostQueryBuilder':
        """查询已发布文章"""
        return self.where("is_published", "=", True)
    
    def by_author(self, author_id: int) -> 'PostQueryBuilder':
        """查询指定作者的文章"""
        return self.where("author_id", "=", author_id)
    
    def by_title_keyword(self, keyword: str) -> 'PostQueryBuilder':
        """根据标题关键词查询"""
        return self.where_like("title", keyword)
    
    def recent_posts(self, days: int = 7) -> 'PostQueryBuilder':
        """查询最近几天的文章"""
        from datetime import datetime, timedelta
        date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
        return self.where("created_at", ">=", date_threshold)
    
    def with_author_info(self) -> 'PostQueryBuilder':
        """关联作者信息"""
        return self.inner_join(
            "users",
            "posts.author_id = users.id"
        ).select([
            "posts.*",
            "users.username as author_username",
            "users.email as author_email"
        ])
    
    def popular_posts(self, limit: int = 10) -> 'PostQueryBuilder':
        """热门文章（这里假设有阅读量字段，实际需要根据业务调整）"""
        return self.published().order_by("created_at", "DESC").limit(limit)


# 使用示例函数
async def query_examples():
    """查询示例"""
    
    # 1. 查询活跃用户及其资料
    active_users_with_profile = await (
        UserQueryBuilder()
        .active_users()
        .with_profile()
        .order_by("created_at", "DESC")
        .limit(20)
        .execute()
    )
    
    # 2. 查询发文章最多的前10位作者
    top_authors = await (
        UserQueryBuilder()
        .top_authors(10)
        .execute()
    )
    
    # 3. 查询最近7天的已发布文章及作者信息
    recent_published_posts = await (
        PostQueryBuilder()
        .published()
        .recent_posts(7)
        .with_author_info()
        .order_by("posts.created_at", "DESC")
        .execute()
    )
    
    # 4. 复杂条件查询：查询gmail用户的已发布文章
    gmail_user_posts = await (
        PostQueryBuilder()
        .published()
        .inner_join("users", "posts.author_id = users.id")
        .where("users.email", "LIKE", "%@gmail.com")
        .select([
            "posts.title",
            "posts.created_at",
            "users.username"
        ])
        .order_by("posts.created_at", "DESC")
        .execute()
    )
    
    return {
        "active_users_with_profile": active_users_with_profile,
        "top_authors": top_authors,
        "recent_published_posts": recent_published_posts,
        "gmail_user_posts": gmail_user_posts
    }