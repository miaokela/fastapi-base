"""
Admin 管理视图
提供用户管理和定时任务管理的API接口
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from tortoise.expressions import Q

from app.core.deps import get_current_active_user, get_current_superuser
from app.core.security import get_password_hash
from app.models.models import (
    User, UserProfile,
    IntervalSchedule, CrontabSchedule, PeriodicTask, TaskResult
)
from app.services.task_scheduler import TaskSchedulerService
from .schemas import (
    # 用户管理
    UserAdminCreate, UserAdminUpdate, UserAdminResponse, UserListResponse,
    # 间隔调度
    IntervalScheduleCreate, IntervalScheduleResponse,
    # Crontab调度
    CrontabScheduleCreate, CrontabScheduleResponse,
    # 定时任务
    PeriodicTaskCreate, PeriodicTaskUpdate, PeriodicTaskResponse, PeriodicTaskListResponse,
    # 任务结果
    TaskResultResponse, TaskResultListResponse,
    # 统计
    TaskStatisticsResponse,
    # 可用任务
    AvailableTaskResponse,
)


router = APIRouter(prefix="/admin", tags=["Admin 管理"])


# ============================================================================
# 管理员权限检查
# ============================================================================

async def check_admin_permission(current_user: User = Depends(get_current_active_user)):
    """检查管理员权限"""
    if not (current_user.is_superuser or current_user.is_staff):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


# ============================================================================
# 用户管理
# ============================================================================

@router.get("/users", response_model=UserListResponse, summary="获取用户列表")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(check_admin_permission)
):
    """获取用户列表（管理员）"""
    query = User.all()
    
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    if search:
        query = query.filter(Q(username__icontains=search) | Q(email__icontains=search))
    
    total = await query.count()
    users = await query.offset(skip).limit(limit).order_by("-created_at")
    
    return UserListResponse(
        total=total,
        items=[UserAdminResponse.model_validate(u, from_attributes=True) for u in users]
    )


@router.post("/users", response_model=UserAdminResponse, status_code=status.HTTP_201_CREATED, summary="创建用户")
async def create_user(
    user_data: UserAdminCreate,
    current_user: User = Depends(get_current_superuser)
):
    """创建新用户（仅超级管理员）"""
    # 检查用户名是否存在
    if await User.filter(username=user_data.username).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否存在
    if await User.filter(email=user_data.email).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    user = await User.create(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=user_data.is_active,
        is_superuser=user_data.is_superuser,
        is_staff=user_data.is_staff
    )
    
    # 创建用户资料
    await UserProfile.create(user=user)
    
    return UserAdminResponse.model_validate(user, from_attributes=True)


@router.get("/users/{user_id}", response_model=UserAdminResponse, summary="获取用户详情")
async def get_user(
    user_id: int,
    current_user: User = Depends(check_admin_permission)
):
    """获取用户详情"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return UserAdminResponse.model_validate(user, from_attributes=True)


@router.put("/users/{user_id}", response_model=UserAdminResponse, summary="更新用户")
async def update_user(
    user_id: int,
    user_data: UserAdminUpdate,
    current_user: User = Depends(get_current_superuser)
):
    """更新用户信息（仅超级管理员）"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    # 检查用户名唯一性
    if "username" in update_data:
        if await User.filter(username=update_data["username"]).exclude(id=user_id).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
    
    # 检查邮箱唯一性
    if "email" in update_data:
        if await User.filter(email=update_data["email"]).exclude(id=user_id).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    # 处理密码
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # 更新用户
    for key, value in update_data.items():
        setattr(user, key, value)
    await user.save()
    
    return UserAdminResponse.model_validate(user, from_attributes=True)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除用户")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser)
):
    """删除用户（仅超级管理员）"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    await user.delete()
    return None


# ============================================================================
# 间隔调度管理
# ============================================================================

@router.get("/schedules/intervals", response_model=List[IntervalScheduleResponse], summary="获取间隔调度列表")
async def list_intervals(
    current_user: User = Depends(check_admin_permission)
):
    """获取所有间隔调度"""
    intervals = await TaskSchedulerService.list_intervals()
    result = []
    for interval in intervals:
        resp = IntervalScheduleResponse(
            id=interval.id,
            every=interval.every,
            period=interval.period,
            display=f"每 {interval.every} {interval.period}"
        )
        result.append(resp)
    return result


@router.post("/schedules/intervals", response_model=IntervalScheduleResponse, status_code=status.HTTP_201_CREATED, summary="创建间隔调度")
async def create_interval(
    data: IntervalScheduleCreate,
    current_user: User = Depends(check_admin_permission)
):
    """创建间隔调度"""
    try:
        interval = await TaskSchedulerService.create_interval(
            every=data.every,
            period=data.period
        )
        return IntervalScheduleResponse(
            id=interval.id,
            every=interval.every,
            period=interval.period,
            display=f"每 {interval.every} {interval.period}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/schedules/intervals/{interval_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除间隔调度")
async def delete_interval(
    interval_id: int,
    current_user: User = Depends(check_admin_permission)
):
    """删除间隔调度"""
    if not await TaskSchedulerService.delete_interval(interval_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="间隔调度不存在"
        )
    return None


# ============================================================================
# Crontab 调度管理
# ============================================================================

@router.get("/schedules/crontabs", response_model=List[CrontabScheduleResponse], summary="获取Crontab调度列表")
async def list_crontabs(
    current_user: User = Depends(check_admin_permission)
):
    """获取所有 Crontab 调度"""
    crontabs = await TaskSchedulerService.list_crontabs()
    result = []
    for crontab in crontabs:
        resp = CrontabScheduleResponse(
            id=crontab.id,
            minute=crontab.minute,
            hour=crontab.hour,
            day_of_week=crontab.day_of_week,
            day_of_month=crontab.day_of_month,
            month_of_year=crontab.month_of_year,
            timezone=crontab.timezone,
            display=str(crontab)
        )
        result.append(resp)
    return result


@router.post("/schedules/crontabs", response_model=CrontabScheduleResponse, status_code=status.HTTP_201_CREATED, summary="创建Crontab调度")
async def create_crontab(
    data: CrontabScheduleCreate,
    current_user: User = Depends(check_admin_permission)
):
    """创建 Crontab 调度"""
    crontab = await TaskSchedulerService.create_crontab(
        minute=data.minute,
        hour=data.hour,
        day_of_week=data.day_of_week,
        day_of_month=data.day_of_month,
        month_of_year=data.month_of_year,
        timezone=data.timezone
    )
    return CrontabScheduleResponse(
        id=crontab.id,
        minute=crontab.minute,
        hour=crontab.hour,
        day_of_week=crontab.day_of_week,
        day_of_month=crontab.day_of_month,
        month_of_year=crontab.month_of_year,
        timezone=crontab.timezone,
        display=str(crontab)
    )


@router.delete("/schedules/crontabs/{crontab_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除Crontab调度")
async def delete_crontab(
    crontab_id: int,
    current_user: User = Depends(check_admin_permission)
):
    """删除 Crontab 调度"""
    if not await TaskSchedulerService.delete_crontab(crontab_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crontab调度不存在"
        )
    return None


# ============================================================================
# 定时任务管理
# ============================================================================

@router.get("/tasks", response_model=PeriodicTaskListResponse, summary="获取定时任务列表")
async def list_periodic_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    enabled: Optional[bool] = None,
    current_user: User = Depends(check_admin_permission)
):
    """获取定时任务列表"""
    tasks = await TaskSchedulerService.list_periodic_tasks(
        enabled=enabled,
        limit=limit,
        offset=skip
    )
    
    total = await PeriodicTask.all().count()
    
    items = []
    for task in tasks:
        item = PeriodicTaskResponse(
            id=task.id,
            name=task.name,
            task=task.task,
            interval_id=task.interval_id,
            interval_display=str(task.interval) if task.interval else None,
            crontab_id=task.crontab_id,
            crontab_display=str(task.crontab) if task.crontab else None,
            args=task.args,
            kwargs=task.kwargs,
            queue=task.queue,
            priority=task.priority,
            expires=task.expires,
            one_off=task.one_off,
            start_time=task.start_time,
            enabled=task.enabled,
            last_run_at=task.last_run_at,
            total_run_count=task.total_run_count,
            description=task.description,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        items.append(item)
    
    return PeriodicTaskListResponse(total=total, items=items)


@router.post("/tasks", response_model=PeriodicTaskResponse, status_code=status.HTTP_201_CREATED, summary="创建定时任务")
async def create_periodic_task(
    data: PeriodicTaskCreate,
    current_user: User = Depends(check_admin_permission)
):
    """创建定时任务"""
    try:
        task = await TaskSchedulerService.create_periodic_task(
            name=data.name,
            task=data.task,
            interval_id=data.interval_id,
            crontab_id=data.crontab_id,
            args=data.args,
            kwargs=data.kwargs,
            queue=data.queue,
            priority=data.priority,
            expires=data.expires,
            one_off=data.one_off,
            start_time=data.start_time,
            enabled=data.enabled,
            description=data.description
        )
        
        # 重新获取以包含关联数据
        task = await TaskSchedulerService.get_periodic_task(task.id)
        
        return PeriodicTaskResponse(
            id=task.id,
            name=task.name,
            task=task.task,
            interval_id=task.interval_id,
            interval_display=str(task.interval) if task.interval else None,
            crontab_id=task.crontab_id,
            crontab_display=str(task.crontab) if task.crontab else None,
            args=task.args,
            kwargs=task.kwargs,
            queue=task.queue,
            priority=task.priority,
            expires=task.expires,
            one_off=task.one_off,
            start_time=task.start_time,
            enabled=task.enabled,
            last_run_at=task.last_run_at,
            total_run_count=task.total_run_count,
            description=task.description,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/tasks/{task_id}", response_model=PeriodicTaskResponse, summary="获取定时任务详情")
async def get_periodic_task(
    task_id: int,
    current_user: User = Depends(check_admin_permission)
):
    """获取定时任务详情"""
    task = await TaskSchedulerService.get_periodic_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="定时任务不存在"
        )
    
    return PeriodicTaskResponse(
        id=task.id,
        name=task.name,
        task=task.task,
        interval_id=task.interval_id,
        interval_display=str(task.interval) if task.interval else None,
        crontab_id=task.crontab_id,
        crontab_display=str(task.crontab) if task.crontab else None,
        args=task.args,
        kwargs=task.kwargs,
        queue=task.queue,
        priority=task.priority,
        expires=task.expires,
        one_off=task.one_off,
        start_time=task.start_time,
        enabled=task.enabled,
        last_run_at=task.last_run_at,
        total_run_count=task.total_run_count,
        description=task.description,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put("/tasks/{task_id}", response_model=PeriodicTaskResponse, summary="更新定时任务")
async def update_periodic_task(
    task_id: int,
    data: PeriodicTaskUpdate,
    current_user: User = Depends(check_admin_permission)
):
    """更新定时任务"""
    update_data = data.model_dump(exclude_unset=True)
    
    task = await TaskSchedulerService.update_periodic_task(task_id, **update_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="定时任务不存在"
        )
    
    # 重新获取以包含关联数据
    task = await TaskSchedulerService.get_periodic_task(task.id)
    
    return PeriodicTaskResponse(
        id=task.id,
        name=task.name,
        task=task.task,
        interval_id=task.interval_id,
        interval_display=str(task.interval) if task.interval else None,
        crontab_id=task.crontab_id,
        crontab_display=str(task.crontab) if task.crontab else None,
        args=task.args,
        kwargs=task.kwargs,
        queue=task.queue,
        priority=task.priority,
        expires=task.expires,
        one_off=task.one_off,
        start_time=task.start_time,
        enabled=task.enabled,
        last_run_at=task.last_run_at,
        total_run_count=task.total_run_count,
        description=task.description,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除定时任务")
async def delete_periodic_task(
    task_id: int,
    current_user: User = Depends(check_admin_permission)
):
    """删除定时任务"""
    if not await TaskSchedulerService.delete_periodic_task(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="定时任务不存在"
        )
    return None


@router.post("/tasks/{task_id}/enable", response_model=dict, summary="启用定时任务")
async def enable_task(
    task_id: int,
    current_user: User = Depends(check_admin_permission)
):
    """启用定时任务"""
    if not await TaskSchedulerService.enable_task(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="定时任务不存在"
        )
    return {"message": "任务已启用"}


@router.post("/tasks/{task_id}/disable", response_model=dict, summary="禁用定时任务")
async def disable_task(
    task_id: int,
    current_user: User = Depends(check_admin_permission)
):
    """禁用定时任务"""
    if not await TaskSchedulerService.disable_task(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="定时任务不存在"
        )
    return {"message": "任务已禁用"}


@router.post("/tasks/{task_id}/run", response_model=dict, summary="立即执行任务")
async def run_task_now(
    task_id: int,
    current_user: User = Depends(check_admin_permission)
):
    """立即执行定时任务"""
    task_result_id = await TaskSchedulerService.run_task_now(task_id)
    if not task_result_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="定时任务不存在"
        )
    return {"message": "任务已提交执行", "task_id": task_result_id}


# ============================================================================
# 任务结果管理
# ============================================================================

@router.get("/results", response_model=TaskResultListResponse, summary="获取任务执行结果列表")
async def list_task_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    task_name: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(check_admin_permission)
):
    """获取任务执行结果列表"""
    results = await TaskSchedulerService.list_task_results(
        task_name=task_name,
        status=status,
        limit=limit,
        offset=skip
    )
    
    query = TaskResult.all()
    if task_name:
        query = query.filter(task_name=task_name)
    if status:
        query = query.filter(status=status)
    total = await query.count()
    
    items = [TaskResultResponse.model_validate(r, from_attributes=True) for r in results]
    
    return TaskResultListResponse(total=total, items=items)


@router.get("/results/{task_id}", response_model=TaskResultResponse, summary="获取任务执行结果详情")
async def get_task_result(
    task_id: str,
    current_user: User = Depends(check_admin_permission)
):
    """获取任务执行结果详情"""
    result = await TaskSchedulerService.get_task_result(task_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务结果不存在"
        )
    return TaskResultResponse.model_validate(result, from_attributes=True)


@router.delete("/results/cleanup", response_model=dict, summary="清理旧的任务结果")
async def cleanup_task_results(
    days: int = Query(30, ge=1, le=365, description="保留最近N天的结果"),
    current_user: User = Depends(get_current_superuser)
):
    """清理旧的任务结果（仅超级管理员）"""
    deleted_count = await TaskSchedulerService.cleanup_old_results(days=days)
    return {"message": f"已清理 {deleted_count} 条旧记录"}


# ============================================================================
# 统计信息
# ============================================================================

@router.get("/statistics", response_model=TaskStatisticsResponse, summary="获取任务统计信息")
async def get_task_statistics(
    current_user: User = Depends(check_admin_permission)
):
    """获取任务统计信息"""
    stats = await TaskSchedulerService.get_task_statistics()
    return TaskStatisticsResponse(**stats)


# ============================================================================
# 可用任务列表
# ============================================================================

@router.get("/available-tasks", response_model=List[AvailableTaskResponse], summary="获取可用任务列表")
async def get_available_tasks(
    current_user: User = Depends(check_admin_permission)
):
    """获取系统中可用的 Celery 任务列表"""
    from celery_app.celery import celery_app
    
    # 获取注册的任务
    registered_tasks = celery_app.tasks.keys()
    
    # 过滤掉内置任务
    available_tasks = []
    for task_name in registered_tasks:
        if not task_name.startswith("celery."):
            available_tasks.append(AvailableTaskResponse(
                name=task_name.split(".")[-1],
                path=task_name,
                description=None
            ))
    
    return available_tasks
