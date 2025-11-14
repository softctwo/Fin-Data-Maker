"""
数据生成进度监控器
提供实时进度跟踪、事件回调和进度报告功能
"""

from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time


class ProgressEventType(Enum):
    """进度事件类型"""
    STARTED = "started"                    # 开始生成
    PROGRESS = "progress"                  # 进度更新
    TABLE_STARTED = "table_started"        # 表生成开始
    TABLE_COMPLETED = "table_completed"    # 表生成完成
    BATCH_COMPLETED = "batch_completed"    # 批次完成
    VALIDATION_STARTED = "validation_started"  # 验证开始
    VALIDATION_COMPLETED = "validation_completed"  # 验证完成
    COMPLETED = "completed"                # 全部完成
    ERROR = "error"                        # 错误发生
    CANCELLED = "cancelled"                # 取消操作


@dataclass
class ProgressEvent:
    """进度事件"""
    event_type: ProgressEventType
    timestamp: datetime
    table_name: Optional[str] = None
    current: int = 0          # 当前进度
    total: int = 0            # 总量
    percentage: float = 0.0   # 完成百分比
    message: str = ""         # 事件消息
    elapsed_time: float = 0.0  # 已用时间（秒）
    eta: float = 0.0          # 预计剩余时间（秒）
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据

    def __str__(self):
        if self.event_type == ProgressEventType.PROGRESS:
            return f"[{self.percentage:.1f}%] {self.message} ({self.current}/{self.total})"
        else:
            return f"[{self.event_type.value}] {self.message}"


class ProgressMonitor:
    """
    进度监控器
    跟踪数据生成进度并触发事件回调
    """

    def __init__(self):
        """初始化进度监控器"""
        self.callbacks: list[Callable[[ProgressEvent], None]] = []
        self.start_time: Optional[float] = None
        self.is_running: bool = False
        self.is_cancelled: bool = False
        self.current_table: Optional[str] = None
        self.total_items: int = 0
        self.completed_items: int = 0
        self.history: list[ProgressEvent] = []
        self.max_history: int = 1000  # 最多保存1000条历史记录

    def add_callback(self, callback: Callable[[ProgressEvent], None]):
        """
        添加事件回调函数

        Args:
            callback: 回调函数，接收ProgressEvent参数
        """
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[ProgressEvent], None]):
        """
        移除事件回调函数

        Args:
            callback: 要移除的回调函数
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def start(self, total_items: int, table_name: Optional[str] = None):
        """
        开始监控

        Args:
            total_items: 总项目数
            table_name: 表名
        """
        self.start_time = time.time()
        self.is_running = True
        self.is_cancelled = False
        self.total_items = total_items
        self.completed_items = 0
        self.current_table = table_name

        event = ProgressEvent(
            event_type=ProgressEventType.STARTED,
            timestamp=datetime.now(),
            table_name=table_name,
            total=total_items,
            message=f"开始生成数据: {table_name or '未知表'}, 总计 {total_items} 条"
        )

        self._emit_event(event)

    def update(self, completed: int, message: str = ""):
        """
        更新进度

        Args:
            completed: 已完成的项目数
            message: 进度消息
        """
        if not self.is_running:
            return

        self.completed_items = completed
        elapsed = time.time() - self.start_time if self.start_time else 0
        percentage = (completed / self.total_items * 100) if self.total_items > 0 else 0

        # 计算ETA
        eta = 0.0
        if completed > 0 and self.total_items > completed:
            avg_time_per_item = elapsed / completed
            remaining_items = self.total_items - completed
            eta = avg_time_per_item * remaining_items

        event = ProgressEvent(
            event_type=ProgressEventType.PROGRESS,
            timestamp=datetime.now(),
            table_name=self.current_table,
            current=completed,
            total=self.total_items,
            percentage=percentage,
            message=message or f"正在生成数据...",
            elapsed_time=elapsed,
            eta=eta
        )

        self._emit_event(event)

    def table_started(self, table_name: str, total_items: int):
        """
        表生成开始

        Args:
            table_name: 表名
            total_items: 总项目数
        """
        self.current_table = table_name
        self.total_items = total_items
        self.completed_items = 0

        event = ProgressEvent(
            event_type=ProgressEventType.TABLE_STARTED,
            timestamp=datetime.now(),
            table_name=table_name,
            total=total_items,
            message=f"开始生成表 {table_name}，总计 {total_items} 条记录"
        )

        self._emit_event(event)

    def table_completed(self, table_name: str, total_items: int):
        """
        表生成完成

        Args:
            table_name: 表名
            total_items: 完成的项目数
        """
        elapsed = time.time() - self.start_time if self.start_time else 0

        event = ProgressEvent(
            event_type=ProgressEventType.TABLE_COMPLETED,
            timestamp=datetime.now(),
            table_name=table_name,
            current=total_items,
            total=total_items,
            percentage=100.0,
            message=f"表 {table_name} 生成完成，共 {total_items} 条记录",
            elapsed_time=elapsed
        )

        self._emit_event(event)

    def batch_completed(self, batch_size: int, batch_num: int):
        """
        批次完成

        Args:
            batch_size: 批次大小
            batch_num: 批次编号
        """
        self.completed_items += batch_size

        event = ProgressEvent(
            event_type=ProgressEventType.BATCH_COMPLETED,
            timestamp=datetime.now(),
            table_name=self.current_table,
            current=self.completed_items,
            total=self.total_items,
            percentage=(self.completed_items / self.total_items * 100) if self.total_items > 0 else 0,
            message=f"批次 #{batch_num} 完成，已生成 {batch_size} 条记录",
            metadata={"batch_size": batch_size, "batch_num": batch_num}
        )

        self._emit_event(event)

    def validation_started(self, item_count: int):
        """
        验证开始

        Args:
            item_count: 要验证的项目数
        """
        event = ProgressEvent(
            event_type=ProgressEventType.VALIDATION_STARTED,
            timestamp=datetime.now(),
            table_name=self.current_table,
            total=item_count,
            message=f"开始验证数据，共 {item_count} 条记录"
        )

        self._emit_event(event)

    def validation_completed(self, item_count: int, is_valid: bool, error_count: int = 0):
        """
        验证完成

        Args:
            item_count: 验证的项目数
            is_valid: 是否验证通过
            error_count: 错误数量
        """
        status = "通过" if is_valid else f"失败（{error_count} 个错误）"

        event = ProgressEvent(
            event_type=ProgressEventType.VALIDATION_COMPLETED,
            timestamp=datetime.now(),
            table_name=self.current_table,
            total=item_count,
            percentage=100.0,
            message=f"数据验证完成：{status}",
            metadata={"is_valid": is_valid, "error_count": error_count}
        )

        self._emit_event(event)

    def complete(self, message: str = "数据生成完成"):
        """
        完成监控

        Args:
            message: 完成消息
        """
        if not self.is_running:
            return

        elapsed = time.time() - self.start_time if self.start_time else 0
        self.is_running = False

        event = ProgressEvent(
            event_type=ProgressEventType.COMPLETED,
            timestamp=datetime.now(),
            table_name=self.current_table,
            current=self.completed_items,
            total=self.total_items,
            percentage=100.0,
            message=message,
            elapsed_time=elapsed
        )

        self._emit_event(event)

    def error(self, error_message: str, exception: Optional[Exception] = None):
        """
        报告错误

        Args:
            error_message: 错误消息
            exception: 异常对象
        """
        self.is_running = False

        metadata = {}
        if exception:
            metadata["exception_type"] = type(exception).__name__
            metadata["exception_message"] = str(exception)

        event = ProgressEvent(
            event_type=ProgressEventType.ERROR,
            timestamp=datetime.now(),
            table_name=self.current_table,
            message=f"错误: {error_message}",
            metadata=metadata
        )

        self._emit_event(event)

    def cancel(self):
        """取消操作"""
        if not self.is_running:
            return

        self.is_running = False
        self.is_cancelled = True

        event = ProgressEvent(
            event_type=ProgressEventType.CANCELLED,
            timestamp=datetime.now(),
            table_name=self.current_table,
            current=self.completed_items,
            total=self.total_items,
            message="操作已取消"
        )

        self._emit_event(event)

    def _emit_event(self, event: ProgressEvent):
        """
        触发事件

        Args:
            event: 进度事件
        """
        # 添加到历史记录
        self.history.append(event)

        # 限制历史记录大小
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        # 调用所有回调函数
        for callback in self.callbacks:
            try:
                callback(event)
            except Exception as e:
                # 回调函数出错不应中断主流程
                print(f"警告: 进度回调函数出错: {e}")

    def get_current_progress(self) -> Dict[str, Any]:
        """
        获取当前进度状态

        Returns:
            Dict: 当前进度信息
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        percentage = (self.completed_items / self.total_items * 100) if self.total_items > 0 else 0

        eta = 0.0
        if self.completed_items > 0 and self.total_items > self.completed_items:
            avg_time_per_item = elapsed / self.completed_items
            remaining_items = self.total_items - self.completed_items
            eta = avg_time_per_item * remaining_items

        return {
            "is_running": self.is_running,
            "is_cancelled": self.is_cancelled,
            "current_table": self.current_table,
            "completed_items": self.completed_items,
            "total_items": self.total_items,
            "percentage": percentage,
            "elapsed_time": elapsed,
            "eta": eta,
        }

    def get_summary(self) -> str:
        """
        获取进度摘要

        Returns:
            str: 格式化的进度摘要
        """
        progress = self.get_current_progress()

        lines = []
        lines.append("=" * 50)
        lines.append("进度摘要")
        lines.append("=" * 50)
        lines.append(f"状态: {'运行中' if progress['is_running'] else '已停止'}")
        lines.append(f"当前表: {progress['current_table'] or '无'}")
        lines.append(f"进度: {progress['completed_items']}/{progress['total_items']} "
                    f"({progress['percentage']:.1f}%)")
        lines.append(f"已用时间: {self._format_time(progress['elapsed_time'])}")

        if progress['is_running'] and progress['eta'] > 0:
            lines.append(f"预计剩余: {self._format_time(progress['eta'])}")

        lines.append("=" * 50)

        return "\n".join(lines)

    def _format_time(self, seconds: float) -> str:
        """
        格式化时间

        Args:
            seconds: 秒数

        Returns:
            str: 格式化的时间字符串
        """
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"


# 预定义的回调函数

def console_callback(event: ProgressEvent):
    """
    控制台输出回调
    在控制台打印进度信息

    Args:
        event: 进度事件
    """
    timestamp = event.timestamp.strftime("%H:%M:%S")
    print(f"[{timestamp}] {event}")


def simple_progress_bar_callback(event: ProgressEvent):
    """
    简单进度条回调
    显示文本进度条

    Args:
        event: 进度事件
    """
    if event.event_type == ProgressEventType.PROGRESS:
        bar_length = 40
        filled_length = int(bar_length * event.percentage / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f'\r进度: |{bar}| {event.percentage:.1f}% {event.message}', end='', flush=True)
    elif event.event_type in (ProgressEventType.COMPLETED, ProgressEventType.ERROR):
        print()  # 换行
