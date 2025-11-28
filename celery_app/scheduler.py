"""
自定义 Celery Beat 调度器
从数据库读取定时任务配置，类似 django-celery-beat
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from celery.beat import Scheduler, ScheduleEntry
from celery.utils.log import get_logger
from tortoise import Tortoise

from config.database import DATABASE_CONFIG

logger = get_logger(__name__)


class DatabaseScheduleEntry(ScheduleEntry):
    """数据库调度条目"""
    
    def __init__(self, task_model, **kwargs):
        self.task_model = task_model
        self.model_id = task_model.id
        
        # 获取调度
        if task_model.interval:
            schedule = task_model.interval.schedule
        elif task_model.crontab:
            schedule = task_model.crontab.schedule
        else:
            from celery.schedules import schedule as celery_schedule
            schedule = celery_schedule(run_every=60)
        
        # 获取参数
        args = task_model.get_args()
        kwargs_dict = task_model.get_kwargs()
        
        # 构建 options
        options = {}
        if task_model.queue:
            options['queue'] = task_model.queue
        if task_model.priority is not None:
            options['priority'] = task_model.priority
        if task_model.expires:
            options['expires'] = task_model.expires
        
        super().__init__(
            name=task_model.name,
            task=task_model.task,
            schedule=schedule,
            args=tuple(args),
            kwargs=kwargs_dict,
            options=options,
            last_run_at=task_model.last_run_at,
            total_run_count=task_model.total_run_count,
            app=kwargs.get('app')
        )
    
    def is_due(self):
        """检查任务是否应该执行"""
        return self.schedule.is_due(self.last_run_at or datetime.utcnow())
    
    def __repr__(self):
        return f"<DatabaseScheduleEntry: {self.name} ({self.task})>"


class DatabaseScheduler(Scheduler):
    """
    数据库调度器
    从 SQLite 数据库读取定时任务配置
    """
    
    # 同步间隔（秒）
    sync_every = 5
    
    # 数据变更检查间隔
    UPDATE_INTERVAL = 5
    
    def __init__(self, *args, **kwargs):
        self._schedule: Dict[str, DatabaseScheduleEntry] = {}
        self._last_update: Optional[datetime] = None
        self._initial_read = False
        self._loop = None
        super().__init__(*args, **kwargs)
    
    def _get_or_create_loop(self):
        """获取或创建事件循环"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def _run_async(self, coro):
        """运行异步协程"""
        loop = self._get_or_create_loop()
        return loop.run_until_complete(coro)
    
    async def _init_db(self):
        """初始化数据库连接"""
        if not Tortoise._inited:
            await Tortoise.init(config=DATABASE_CONFIG)
            logger.info("Database connection initialized for scheduler")
    
    async def _close_db(self):
        """关闭数据库连接"""
        await Tortoise.close_connections()
    
    async def _get_changed_marker(self):
        """获取变更标记"""
        from app.models.models import PeriodicTaskChanged
        
        await self._init_db()
        
        try:
            marker = await PeriodicTaskChanged.get_or_none(id=1)
            return marker.last_update if marker else None
        except Exception as e:
            logger.error(f"Error getting change marker: {e}")
            return None
    
    async def _load_entries_from_db(self):
        """从数据库加载任务条目"""
        from app.models.models import PeriodicTask
        
        await self._init_db()
        
        try:
            tasks = await PeriodicTask.filter(enabled=True).prefetch_related("interval", "crontab")
            
            entries = {}
            for task in tasks:
                try:
                    entry = DatabaseScheduleEntry(task, app=self.app)
                    entries[task.name] = entry
                    logger.debug(f"Loaded task: {task.name}")
                except Exception as e:
                    logger.error(f"Error loading task {task.name}: {e}")
            
            return entries
        except Exception as e:
            logger.error(f"Error loading tasks from database: {e}")
            return {}
    
    async def _update_task_run_info(self, task_name: str, last_run_at: datetime, total_run_count: int):
        """更新任务运行信息"""
        from app.models.models import PeriodicTask
        
        await self._init_db()
        
        try:
            task = await PeriodicTask.get_or_none(name=task_name)
            if task:
                task.last_run_at = last_run_at
                task.total_run_count = total_run_count
                await task.save()
        except Exception as e:
            logger.error(f"Error updating task run info: {e}")
    
    def setup_schedule(self):
        """设置调度"""
        logger.info("Setting up database scheduler...")
        self._run_async(self._init_db())
        self._schedule = self._run_async(self._load_entries_from_db())
        self._initial_read = True
        logger.info(f"Loaded {len(self._schedule)} tasks from database")
    
    @property
    def schedule(self):
        """获取调度表"""
        if not self._initial_read:
            self.setup_schedule()
        
        # 检查是否需要更新
        self._maybe_refresh()
        
        return self._schedule
    
    def _maybe_refresh(self):
        """检查并刷新调度表"""
        now = datetime.utcnow()
        
        if self._last_update is None:
            self._last_update = now
            return
        
        # 检查是否超过更新间隔
        if (now - self._last_update).total_seconds() < self.UPDATE_INTERVAL:
            return
        
        self._last_update = now
        
        # 检查数据库变更
        try:
            self._schedule = self._run_async(self._load_entries_from_db())
            logger.debug(f"Refreshed schedule, {len(self._schedule)} tasks loaded")
        except Exception as e:
            logger.error(f"Error refreshing schedule: {e}")
    
    def sync(self):
        """同步任务运行状态到数据库"""
        for name, entry in self._schedule.items():
            if entry.last_run_at and entry.total_run_count > 0:
                try:
                    self._run_async(
                        self._update_task_run_info(
                            name,
                            entry.last_run_at,
                            entry.total_run_count
                        )
                    )
                except Exception as e:
                    logger.error(f"Error syncing task {name}: {e}")
    
    def close(self):
        """关闭调度器"""
        self.sync()
        self._run_async(self._close_db())
        super().close()
    
    @property
    def info(self):
        """调度器信息"""
        return f"DatabaseScheduler: {len(self._schedule)} tasks"
