"""
数据库模型
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import secrets

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
    batch_tasks = db.relationship('BatchTask', backref='user', lazy=True, cascade='all, delete-orphan')
    api_tokens = db.relationship('APIToken', backref='user', lazy=True, cascade='all, delete-orphan')

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


class BatchTask(db.Model):
    """批量任务模型"""
    __tablename__ = 'batch_tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    db_config = db.Column(db.Text, nullable=False)  # JSON格式的数据库配置
    tables = db.Column(db.Text, nullable=False)  # JSON格式的表列表
    generation_config = db.Column(db.Text)  # JSON格式的生成配置
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed, cancelled
    total_tables = db.Column(db.Integer, default=0)
    completed_tables = db.Column(db.Integer, default=0)
    failed_tables = db.Column(db.Integer, default=0)
    progress = db.Column(db.Integer, default=0)  # 进度百分比 0-100
    results = db.Column(db.Text)  # JSON格式的详细结果
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'db_config': json.loads(self.db_config) if self.db_config else {},
            'tables': json.loads(self.tables) if self.tables else [],
            'generation_config': json.loads(self.generation_config) if self.generation_config else {},
            'status': self.status,
            'total_tables': self.total_tables,
            'completed_tables': self.completed_tables,
            'failed_tables': self.failed_tables,
            'progress': self.progress,
            'results': json.loads(self.results) if self.results else {},
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class APIToken(db.Model):
    """API令牌模型"""
    __tablename__ = 'api_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    scopes = db.Column(db.Text)  # JSON格式的权限范围列表
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    last_used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_token():
        """生成随机令牌"""
        return secrets.token_urlsafe(48)

    def is_expired(self):
        """检查令牌是否已过期"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """检查令牌是否有效"""
        return self.is_active and not self.is_expired()

    def has_scope(self, scope):
        """检查令牌是否具有特定权限"""
        if not self.scopes:
            return False
        scopes_list = json.loads(self.scopes) if isinstance(self.scopes, str) else self.scopes
        return scope in scopes_list

    def update_last_used(self):
        """更新最后使用时间"""
        self.last_used_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self, include_token=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'scopes': json.loads(self.scopes) if self.scopes else [],
            'is_active': self.is_active,
            'is_expired': self.is_expired(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_token:
            data['token'] = self.token
        return data
