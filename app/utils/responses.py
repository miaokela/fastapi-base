"""
API响应格式标准化模块
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """标准API响应格式"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """分页响应格式"""
    success: bool = True
    message: str = "查询成功"
    data: List[Any] = []
    pagination: Dict[str, Any] = {}
    errors: Optional[List[str]] = None


def success_response(
    data: Any = None,
    message: str = "操作成功",
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """成功响应"""
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    
    if meta:
        response["meta"] = meta
    
    return response


def error_response(
    message: str = "操作失败",
    errors: Optional[List[str]] = None,
    data: Any = None
) -> Dict[str, Any]:
    """错误响应"""
    response = {
        "success": False,
        "message": message,
        "data": data
    }
    
    if errors:
        response["errors"] = errors
    
    return response


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "查询成功"
) -> Dict[str, Any]:
    """分页响应"""
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "success": True,
        "message": message,
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


def validation_error_response(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """验证错误响应"""
    error_messages = []
    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    return error_response(
        message="数据验证失败",
        errors=error_messages
    )