"""
用户认证模块
"""

from flask_login import LoginManager
from flask import request, jsonify
from functools import wraps
from .models import User, APIToken

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'


@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    return User.query.get(int(user_id))


def token_required(scopes=None):
    """
    API令牌认证装饰器

    Args:
        scopes: 需要的权限范围列表
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 从请求头获取令牌
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                return jsonify({'success': False, 'message': '缺少Authorization头'}), 401

            # 解析令牌
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'success': False, 'message': '无效的Authorization头格式'}), 401

            token_string = parts[1]

            # 查找令牌
            token = APIToken.query.filter_by(token=token_string).first()

            if not token:
                return jsonify({'success': False, 'message': '无效的令牌'}), 401

            # 检查令牌是否有效
            if not token.is_valid():
                return jsonify({'success': False, 'message': '令牌已过期或被禁用'}), 401

            # 检查权限范围
            if scopes:
                for scope in scopes:
                    if not token.has_scope(scope):
                        return jsonify({'success': False, 'message': f'缺少权限: {scope}'}), 403

            # 更新最后使用时间
            token.update_last_used()

            # 将令牌和用户添加到请求上下文
            request.api_token = token
            request.api_user = token.user

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def get_token_from_request():
    """从请求中获取令牌对象"""
    return getattr(request, 'api_token', None)


def get_user_from_token():
    """从令牌获取用户对象"""
    return getattr(request, 'api_user', None)
