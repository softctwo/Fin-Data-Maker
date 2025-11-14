"""
定时任务调度器
用于管理和执行定时数据生成任务
"""

import json
import traceback
from datetime import datetime, timedelta
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from src.datasource.db_connector import DatabaseConnector, DatabaseType
from src.datasource.metadata_extractor import MetadataExtractor
from src.datasource.data_profiler import DataProfiler
from src.core.app import DataMakerApp


class TaskScheduler:
    """任务调度器"""

    def __init__(self, scheduler, db_session):
        """
        初始化任务调度器

        Args:
            scheduler: APScheduler实例
            db_session: 数据库会话
        """
        self.scheduler = scheduler
        self.db_session = db_session

    def add_scheduled_task(self, task_id: int):
        """
        添加定时任务到调度器

        Args:
            task_id: 任务ID
        """
        from src.web.models import ScheduledTask

        task = self.db_session.query(ScheduledTask).get(task_id)
        if not task or task.status != 'active':
            return

        # 根据调度类型创建触发器
        trigger = self._create_trigger(task.schedule_type, task.schedule_time)

        if not trigger:
            return

        # 添加任务到调度器
        job_id = f'scheduled_task_{task_id}'

        # 如果任务已存在，先移除
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        self.scheduler.add_job(
            func=self._execute_task,
            trigger=trigger,
            args=[task_id],
            id=job_id,
            replace_existing=True,
            max_instances=1
        )

        # 更新下次运行时间
        next_run = self.scheduler.get_job(job_id).next_run_time
        task.next_run = next_run
        self.db_session.commit()

    def remove_scheduled_task(self, task_id: int):
        """
        从调度器中移除任务

        Args:
            task_id: 任务ID
        """
        job_id = f'scheduled_task_{task_id}'

        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

    def _create_trigger(self, schedule_type: str, schedule_time: str):
        """
        创建触发器

        Args:
            schedule_type: 调度类型 (once, daily, weekly, monthly)
            schedule_time: 时间表达式

        Returns:
            触发器对象
        """
        try:
            if schedule_type == 'once':
                # 一次性任务，使用DateTrigger
                run_date = datetime.fromisoformat(schedule_time)
                return DateTrigger(run_date=run_date)

            elif schedule_type == 'daily':
                # 每日任务，格式: "HH:MM"
                hour, minute = map(int, schedule_time.split(':'))
                return CronTrigger(hour=hour, minute=minute)

            elif schedule_type == 'weekly':
                # 每周任务，格式: "weekday HH:MM" (weekday: 0-6, 0=Monday)
                parts = schedule_time.split()
                weekday = int(parts[0])
                hour, minute = map(int, parts[1].split(':'))
                return CronTrigger(day_of_week=weekday, hour=hour, minute=minute)

            elif schedule_type == 'monthly':
                # 每月任务，格式: "day HH:MM" (day: 1-31)
                parts = schedule_time.split()
                day = int(parts[0])
                hour, minute = map(int, parts[1].split(':'))
                return CronTrigger(day=day, hour=hour, minute=minute)

        except Exception as e:
            print(f"创建触发器失败: {str(e)}")
            return None

    def _execute_task(self, task_id: int):
        """
        执行定时任务

        Args:
            task_id: 任务ID
        """
        from src.web.models import ScheduledTask, Config, History

        try:
            # 获取任务信息
            task = self.db_session.query(ScheduledTask).get(task_id)
            if not task or task.status != 'active':
                return

            # 获取配置
            config = self.db_session.query(Config).get(task.config_id)
            if not config:
                return

            # 解析配置
            db_config = json.loads(config.db_config)
            generation_config = json.loads(config.generation_config) if config.generation_config else {}

            # 连接数据库
            db_type = DatabaseType[db_config.get('type', 'mysql').upper()]
            connector = DatabaseConnector(
                db_type=db_type,
                host=db_config.get('host'),
                port=db_config.get('port'),
                database=db_config.get('database'),
                username=db_config.get('username'),
                password=db_config.get('password')
            )

            connector.connect()

            # 提取表结构
            extractor = MetadataExtractor(connector)
            table = extractor.extract_table(config.table_name)

            if not table:
                raise Exception(f"表 {config.table_name} 不存在或无法提取")

            # 数据质量分析（如果需要）
            if generation_config.get('analyze_quality', False):
                profiler = DataProfiler(connector)
                sample_size = generation_config.get('sample_size', 1000)
                strictness = generation_config.get('strictness', 'medium')

                profiles = profiler.profile_table(table, sample_size=sample_size)
                table = profiler.update_table_metadata(table, profiles)
                rules = profiler.generate_quality_rules(table, profiles, strictness=strictness)

            # 生成数据
            seed = generation_config.get('seed')
            app = DataMakerApp(seed=seed) if seed else DataMakerApp()

            if generation_config.get('analyze_quality', False):
                for rule in rules:
                    app.add_rule(rule)

            app.add_table(table)

            count = generation_config.get('count', 1000)
            data, validation_report = app.generate_data(
                config.table_name,
                count=count,
                validate=generation_config.get('validate', True)
            )

            # 关闭连接
            connector.close()

            # 更新任务状态
            task.last_run = datetime.utcnow()
            task.status = 'completed' if task.schedule_type == 'once' else 'active'

            # 更新下次运行时间
            if task.status == 'active':
                job = self.scheduler.get_job(f'scheduled_task_{task_id}')
                if job:
                    task.next_run = job.next_run_time

            # 记录历史
            history = History(
                user_id=task.user_id,
                operation_type='scheduled_generate',
                table_name=config.table_name,
                record_count=len(data),
                status='success',
                details=json.dumps({
                    'task_id': task_id,
                    'task_name': task.name,
                    'validation_report': {
                        'total_rows': validation_report.total_rows,
                        'valid_rows': validation_report.valid_rows,
                        'error_count': len(validation_report.errors),
                        'warning_count': len(validation_report.warnings)
                    }
                }, ensure_ascii=False)
            )
            self.db_session.add(history)
            self.db_session.commit()

        except Exception as e:
            # 记录失败历史
            try:
                history = History(
                    user_id=task.user_id,
                    operation_type='scheduled_generate',
                    table_name=config.table_name if config else None,
                    status='failed',
                    details=json.dumps({
                        'task_id': task_id,
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }, ensure_ascii=False)
                )
                self.db_session.add(history)

                # 更新任务状态
                task.last_run = datetime.utcnow()
                task.status = 'failed'

                self.db_session.commit()

            except Exception as inner_e:
                print(f"记录定时任务失败历史时出错: {str(inner_e)}")

    def load_all_tasks(self):
        """加载所有激活的定时任务到调度器"""
        from src.web.models import ScheduledTask

        tasks = self.db_session.query(ScheduledTask).filter_by(status='active').all()

        for task in tasks:
            try:
                self.add_scheduled_task(task.id)
                print(f"已加载定时任务: {task.name} (ID: {task.id})")
            except Exception as e:
                print(f"加载定时任务 {task.name} 失败: {str(e)}")


def init_scheduler(app, scheduler):
    """
    初始化调度器，加载所有激活的定时任务

    Args:
        app: Flask应用
        scheduler: APScheduler实例
    """
    with app.app_context():
        from src.web.models import db

        task_scheduler = TaskScheduler(scheduler, db.session)
        task_scheduler.load_all_tasks()

    return task_scheduler
