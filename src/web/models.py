"""
数据库模型
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # 关联
    configs = db.relationship('Config', backref='user', lazy=True, cascade='all, delete-orphan')
    histories = db.relationship('History', backref='user', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('ScheduledTask', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }


class Config(db.Model):
    """生成配置模型"""
    __tablename__ = 'configs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    db_config = db.Column(db.Text, nullable=False)  # JSON格式的数据库配置
    table_name = db.Column(db.String(100))
    generation_config = db.Column(db.Text)  # JSON格式的生成配置
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'db_config': json.loads(self.db_config) if self.db_config else {},
            'table_name': self.table_name,
            'generation_config': json.loads(self.generation_config) if self.generation_config else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class History(db.Model):
    """历史记录模型"""
    __tablename__ = 'histories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    operation_type = db.Column(db.String(50), nullable=False)  # connect, generate, export等
    table_name = db.Column(db.String(100))
    record_count = db.Column(db.Integer)
    status = db.Column(db.String(20))  # success, failed
    details = db.Column(db.Text)  # JSON格式的详细信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'operation_type': self.operation_type,
            'table_name': self.table_name,
            'record_count': self.record_count,
            'status': self.status,
            'details': json.loads(self.details) if self.details else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ScheduledTask(db.Model):
    """定时任务模型"""
    __tablename__ = 'scheduled_tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    config_id = db.Column(db.Integer, db.ForeignKey('configs.id'))
    schedule_type = db.Column(db.String(20), nullable=False)  # once, daily, weekly, monthly
    schedule_time = db.Column(db.String(50))  # 时间表达式
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    config = db.relationship('Config', backref='tasks')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'config_id': self.config_id,
            'schedule_type': self.schedule_type,
            'schedule_time': self.schedule_time,
            'status': self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
