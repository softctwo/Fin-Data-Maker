"""
Web应用模块
"""

from .models import db, User, Config, History, ScheduledTask, BatchTask
from .auth import login_manager

__all__ = ['db', 'User', 'Config', 'History', 'ScheduledTask', 'BatchTask', 'login_manager']
