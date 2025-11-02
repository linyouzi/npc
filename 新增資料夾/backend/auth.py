"""
認證相關功能模組
包含 JWT token 生成、驗證、密碼加密等
"""
import jwt
import bcrypt
import hashlib
from datetime import datetime, timedelta
import secrets
import os

# JWT 密鑰（生產環境應該從環境變數讀取）
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24  # Token 24小時過期

def hash_password(password):
    """使用 bcrypt 加密密碼"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    """驗證密碼"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        # 兼容舊的 SHA256 密碼
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        return sha256_hash == hashed

def generate_token(user_id, username, expiration_hours=None):
    """生成 JWT token"""
    exp_hours = expiration_hours if expiration_hours else JWT_EXPIRATION_HOURS
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=exp_hours),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    # PyJWT 2.x 返回字串，不需要 decode
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token

def verify_token(token):
    """驗證 JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """認證裝飾器，保護需要登錄的路由"""
    from functools import wraps
    from flask import request, jsonify
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 從 Header 獲取 token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': '無效的認證格式'}), 401
        
        # 從 Cookie 獲取 token（備用方案）
        if not token:
            token = request.cookies.get('auth_token')
        
        if not token:
            return jsonify({'message': '未授權，請先登錄'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'message': 'Token 無效或已過期'}), 401
        
        # 將用戶信息添加到請求上下文
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function

