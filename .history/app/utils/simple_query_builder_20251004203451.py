"""
简化的查询构建器实现
由于 query-builder-tool 包不可用，这里提供一个简单的查询构建器实现
"""

from typing import Any, Dict, List, Optional, Union
from tortoise.models import Model
try:
    from tortoise import Tortoise
except ImportError:
    # 如果无法导入 Tortoise，创建一个简单的占位符
    class Tortoise:
        @staticmethod
        def get_connection(name: str):
            raise NotImplementedError("Tortoise ORM 连接不可用")


class SimpleQueryBuilder:
    """简单的查询构建器"""
    
    def __init__(self, model: Optional[Model] = None):
        self.model = model
        self._select_fields = []
        self._where_conditions = []
        self._joins = []
        self._order_by = []
        self._group_by = []
        self._having = None
        self._limit_value = None
        self._offset_value = None
        self._table_name = model._meta.db_table if model else None
    
    def select(self, *fields):
        """选择字段"""
        self._select_fields.extend(fields)
        return self
    
    def where(self, field: str, operator: str, value: Any):
        """添加WHERE条件"""
        self._where_conditions.append(f"{field} {operator} '{value}'")
        return self
    
    def where_in(self, field: str, values: List[Any]):
        """WHERE IN条件"""
        value_str = "', '".join(str(v) for v in values)
        self._where_conditions.append(f"{field} IN ('{value_str}')")
        return self
    
    def where_like(self, field: str, pattern: str):
        """WHERE LIKE条件"""
        self._where_conditions.append(f"{field} LIKE '%{pattern}%'")
        return self
    
    def join(self, table: str, on_condition: str, join_type: str = "INNER"):
        """添加JOIN"""
        self._joins.append(f"{join_type} JOIN {table} ON {on_condition}")
        return self
    
    def left_join(self, table: str, on_condition: str):
        """LEFT JOIN"""
        return self.join(table, on_condition, "LEFT")
    
    def order_by(self, field: str, direction: str = "ASC"):
        """添加ORDER BY"""
        self._order_by.append(f"{field} {direction}")
        return self
    
    def group_by(self, *fields):
        """添加GROUP BY"""
        self._group_by.extend(fields)
        return self
    
    def limit(self, count: int):
        """添加LIMIT"""
        self._limit_value = count
        return self
    
    def offset(self, count: int):
        """添加OFFSET"""
        self._offset_value = count
        return self
    
    def build(self) -> str:
        """构建SQL查询"""
        # SELECT
        if self._select_fields:
            select_clause = f"SELECT {', '.join(self._select_fields)}"
        else:
            select_clause = "SELECT *"
        
        # FROM
        from_clause = f"FROM {self._table_name}" if self._table_name else ""
        
        # JOINs
        join_clause = " ".join(self._joins) if self._joins else ""
        
        # WHERE
        where_clause = f"WHERE {' AND '.join(self._where_conditions)}" if self._where_conditions else ""
        
        # GROUP BY
        group_by_clause = f"GROUP BY {', '.join(self._group_by)}" if self._group_by else ""
        
        # HAVING
        having_clause = f"HAVING {self._having}" if self._having else ""
        
        # ORDER BY
        order_by_clause = f"ORDER BY {', '.join(self._order_by)}" if self._order_by else ""
        
        # LIMIT
        limit_clause = f"LIMIT {self._limit_value}" if self._limit_value else ""
        
        # OFFSET
        offset_clause = f"OFFSET {self._offset_value}" if self._offset_value else ""
        
        # 组合所有子句
        clauses = [
            select_clause,
            from_clause,
            join_clause,
            where_clause,
            group_by_clause,
            having_clause,
            order_by_clause,
            limit_clause,
            offset_clause
        ]
        
        return " ".join(clause for clause in clauses if clause)
    
    async def execute(self) -> List[Dict[str, Any]]:
        """执行查询"""
        sql = self.build()
        connection = Tortoise.get_connection("default")
        result = await connection.execute_query(sql)
        return result[1]  # 返回查询结果


class UserQueryBuilder(SimpleQueryBuilder):
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
    
    def with_email_domain(self, domain: str):
        """查询指定邮箱域名的用户"""
        return self.where_like("email", f"@{domain}")


class PostQueryBuilder(SimpleQueryBuilder):
    """文章查询构建器"""
    
    def __init__(self):
        from app.models.models import Post
        super().__init__(Post)
    
    def published(self):
        """查询已发布文章"""
        return self.where("is_published", "=", True)
    
    def by_author(self, author_id: int):
        """查询指定作者的文章"""
        return self.where("author_id", "=", author_id)
    
    def with_author_info(self):
        """关联作者信息"""
        return self.join("users", "posts.author_id = users.id").select(
            "posts.*", "users.username as author_username"
        )