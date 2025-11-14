"""
批量处理器
用于批量生成多个表的测试数据
"""

import json
import traceback
from datetime import datetime
from threading import Thread
from typing import Dict, List, Any

from src.datasource.db_connector import DatabaseConnector, DatabaseType
from src.datasource.metadata_extractor import MetadataExtractor
from src.datasource.data_profiler import DataProfiler
from src.core.app import DataMakerApp


class BatchProcessor:
    """批量任务处理器"""

    def __init__(self, db_session, batch_task_id: int):
        """
        初始化批量处理器

        Args:
            db_session: 数据库会话
            batch_task_id: 批量任务ID
        """
        self.db_session = db_session
        self.batch_task_id = batch_task_id
        self.connector = None
        self.app = None

    def _update_task_status(self, **kwargs):
        """更新任务状态"""
        from src.web.models import BatchTask

        task = self.db_session.query(BatchTask).get(self.batch_task_id)
        if task:
            for key, value in kwargs.items():
                setattr(task, key, value)
            self.db_session.commit()

    def _connect_database(self, db_config: Dict[str, Any]) -> bool:
        """连接数据库"""
        try:
            db_type_str = db_config.get('type', 'mysql')
            db_type = DatabaseType[db_type_str.upper()]

            self.connector = DatabaseConnector(
                db_type=db_type,
                host=db_config.get('host'),
                port=db_config.get('port'),
                database=db_config.get('database'),
                username=db_config.get('username'),
                password=db_config.get('password')
            )

            self.connector.connect()
            return True
        except Exception as e:
            self._update_task_status(
                status='failed',
                error_message=f'数据库连接失败: {str(e)}',
                completed_at=datetime.utcnow()
            )
            return False

    def _process_single_table(self, table_name: str, generation_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个表

        Returns:
            包含处理结果的字典
        """
        result = {
            'table_name': table_name,
            'status': 'pending',
            'record_count': 0,
            'error': None,
            'validation_report': None
        }

        try:
            # 提取表结构
            extractor = MetadataExtractor(self.connector)
            table = extractor.extract_table(table_name)

            if not table:
                result['status'] = 'failed'
                result['error'] = '表不存在或无法提取表结构'
                return result

            # 数据质量分析（如果需要）
            if generation_config.get('analyze_quality', False):
                profiler = DataProfiler(self.connector)
                sample_size = generation_config.get('sample_size', 1000)
                strictness = generation_config.get('strictness', 'medium')

                profiles = profiler.profile_table(table, sample_size=sample_size)
                table = profiler.update_table_metadata(table, profiles)
                rules = profiler.generate_quality_rules(table, profiles, strictness=strictness)

                # 添加规则到应用
                for rule in rules:
                    self.app.add_rule(rule)

            # 生成数据
            count = generation_config.get('count', 1000)
            seed = generation_config.get('seed')

            if seed is not None:
                self.app = DataMakerApp(seed=seed)
            else:
                self.app = DataMakerApp()

            self.app.add_table(table)

            # 生成数据
            data, validation_report = self.app.generate_data(
                table_name,
                count=count,
                validate=generation_config.get('validate', True)
            )

            result['status'] = 'success'
            result['record_count'] = len(data)
            result['validation_report'] = {
                'total_rows': validation_report.total_rows,
                'valid_rows': validation_report.valid_rows,
                'error_count': len(validation_report.errors),
                'warning_count': len(validation_report.warnings)
            }

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()

        return result

    def process(self):
        """执行批量处理任务"""
        from src.web.models import BatchTask

        # 获取任务信息
        task = self.db_session.query(BatchTask).get(self.batch_task_id)
        if not task:
            return

        # 解析配置
        db_config = json.loads(task.db_config)
        tables = json.loads(task.tables)
        generation_config = json.loads(task.generation_config) if task.generation_config else {}

        # 更新任务状态为运行中
        self._update_task_status(
            status='running',
            started_at=datetime.utcnow(),
            total_tables=len(tables),
            progress=0
        )

        # 连接数据库
        if not self._connect_database(db_config):
            return

        # 处理每个表
        results = {}
        completed = 0
        failed = 0

        for i, table_name in enumerate(tables):
            try:
                # 处理单个表
                result = self._process_single_table(table_name, generation_config)
                results[table_name] = result

                # 更新计数
                if result['status'] == 'success':
                    completed += 1
                else:
                    failed += 1

                # 更新进度
                progress = int(((i + 1) / len(tables)) * 100)
                self._update_task_status(
                    completed_tables=completed,
                    failed_tables=failed,
                    progress=progress,
                    results=json.dumps(results, ensure_ascii=False)
                )

            except Exception as e:
                failed += 1
                results[table_name] = {
                    'table_name': table_name,
                    'status': 'failed',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }

                self._update_task_status(
                    completed_tables=completed,
                    failed_tables=failed,
                    progress=int(((i + 1) / len(tables)) * 100),
                    results=json.dumps(results, ensure_ascii=False)
                )

        # 关闭数据库连接
        if self.connector:
            self.connector.close()

        # 更新最终状态
        final_status = 'completed' if failed == 0 else ('partial' if completed > 0 else 'failed')
        self._update_task_status(
            status=final_status,
            completed_at=datetime.utcnow(),
            progress=100,
            results=json.dumps(results, ensure_ascii=False)
        )


def start_batch_task(db_session, batch_task_id: int):
    """
    在后台线程启动批量任务

    Args:
        db_session: 数据库会话
        batch_task_id: 批量任务ID
    """
    processor = BatchProcessor(db_session, batch_task_id)

    # 在新线程中执行
    thread = Thread(target=processor.process)
    thread.daemon = True
    thread.start()
