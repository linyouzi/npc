from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from models import User, init_db
from auth import hash_password, verify_password, generate_token, verify_token, require_auth
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
CORS(app, supports_credentials=True)  # 允許跨域請求並支持憑證

# 初始化資料庫
init_db()

@app.route('/api/login', methods=['POST'])
def login():
    """登錄 API - 專業版本"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        remember_me = data.get('remember_me', False)
        
        if not username or not password:
            return jsonify({'message': '請輸入帳號和密碼'}), 400
        
        # 獲取客戶端信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        # 檢查用戶是否存在
        user = User.get_by_username(username)
        
        if not user:
            # 記錄失敗（為了安全，不洩露用戶是否存在）
            User.record_login_failure(username, ip_address, user_agent)
            return jsonify({'message': '帳號或密碼錯誤'}), 401
        
        # 檢查帳號是否被鎖定
        if User.is_locked(username):
            return jsonify({
                'message': '帳號因多次登錄失敗已被鎖定，請稍後再試',
                'locked': True
            }), 423  # 423 Locked
        
        # 驗證密碼
        if not verify_password(password, user.password):
            User.record_login_failure(username, ip_address, user_agent)
            return jsonify({'message': '帳號或密碼錯誤'}), 401
        
        # 登錄成功
        User.record_login_success(username, ip_address, user_agent)
        
        # 生成 token
        expiration_hours = 720 if remember_me else 24  # 記住我：30天，否則24小時
        token = generate_token(user.id, user.username, expiration_hours)
        
        # 保存 session
        expires_at = (datetime.now() + timedelta(hours=expiration_hours)).isoformat()
        User.save_session(user.id, token, ip_address, user_agent, expires_at)
        
        response = make_response(jsonify({
            'message': '登入成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'last_login': user.last_login
            },
            'token': token
        }), 200)
        
        # 設置 HTTP-only Cookie（額外安全層）
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            secure=False,  # 生產環境應設為 True（HTTPS）
            samesite='Lax',
            max_age=expiration_hours * 3600
        )
        
        return response
            
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    """登出 API"""
    try:
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        elif request.cookies.get('auth_token'):
            token = request.cookies.get('auth_token')
        
        if token:
            User.delete_session(token)
        
        response = make_response(jsonify({'message': '已成功登出'}), 200)
        response.set_cookie('auth_token', '', expires=0)
        return response
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/auth/verify', methods=['GET'])
@require_auth
def verify_auth():
    """驗證當前認證狀態"""
    try:
        user_id = request.current_user['user_id']
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({'message': '用戶不存在'}), 404
        
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'last_login': user.last_login,
                'created_at': user.created_at
            }
        }), 200
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """註冊 API - 升級版本"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password:
            return jsonify({'message': '請輸入帳號和密碼'}), 400
        
        # 驗證用戶名格式
        if len(username) < 3 or len(username) > 20:
            return jsonify({'message': '用戶名長度應在3-20個字元之間'}), 400
        
        # 驗證密碼強度
        if len(password) < 6:
            return jsonify({'message': '密碼長度至少需要6個字元'}), 400
        
        # 檢查用戶是否已存在
        if User.get_by_username(username):
            return jsonify({'message': '帳號已存在'}), 400
        
        # 創建新用戶（使用 bcrypt 加密）
        hashed_password = hash_password(password)
        User.create(username, hashed_password, email)
        
        return jsonify({'message': '註冊成功'}), 201
        
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/guest-login', methods=['POST'])
def guest_login():
    """訪客登入 API"""
    try:
        import random
        import string
        
        # 生成唯一的訪客帳號
        guest_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        username = f'guest_{guest_id}'
        
        # 檢查是否已存在（極低機率）
        while User.get_by_username(username):
            guest_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            username = f'guest_{guest_id}'
        
        # 生成隨機密碼
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        
        # 創建訪客帳號
        hashed_password = hash_password(password)
        user = User.create(username, hashed_password, None)
        
        # 獲取客戶端信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        # 記錄登錄成功
        User.record_login_success(username, ip_address, user_agent)
        
        # 生成 token（訪客token 24小時有效）
        token = generate_token(user.id, username, 24)
        
        # 保存 session
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        User.save_session(user.id, token, ip_address, user_agent, expires_at)
        
        response = make_response(jsonify({
            'message': '訪客登入成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'isGuest': True
            },
            'token': token
        }), 200)
        
        # 設置 HTTP-only Cookie
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=24 * 3600
        )
        
        return response
        
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/oauth/google', methods=['POST'])
def oauth_google():
    """Google OAuth 登入"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'message': '缺少 Google token'}), 400
        
        # 驗證 Google token
        try:
            # 使用 Google token info endpoint 驗證
            response = requests.get(
                f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}'
            )
            
            if response.status_code != 200:
                return jsonify({'message': '無效的 Google token'}), 401
            
            user_info = response.json()
            
            # 提取用戶信息
            google_id = user_info.get('sub')
            email = user_info.get('email')
            name = user_info.get('name', '')
            picture = user_info.get('picture', '')
            
            if not google_id or not email:
                return jsonify({'message': '無法獲取 Google 用戶信息'}), 400
            
            # 查找或創建用戶
            # 先檢查是否已有相同 email 的用戶
            user = User.get_by_email(email)
            
            if not user:
                # 創建新用戶（使用 Google ID 作為用戶名前綴）
                username = f'google_{google_id[:8]}'
                # 確保用戶名唯一
                original_username = username
                counter = 1
                while User.get_by_username(username):
                    username = f'{original_username}_{counter}'
                    counter += 1
                
                # 使用隨機密碼（OAuth 用戶不需要密碼）
                random_password = secrets.token_urlsafe(32)
                hashed_password = hash_password(random_password)
                user = User.create(username, hashed_password, email)
            
            # 記錄登錄成功
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            User.record_login_success(user.username, ip_address, user_agent)
            
            # 生成 token
            token = generate_token(user.id, user.username, 24)
            
            # 保存 session
            expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
            User.save_session(user.id, token, ip_address, user_agent, expires_at)
            
            response = make_response(jsonify({
                'message': 'Google 登入成功',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'isOAuth': True,
                    'oauthProvider': 'google'
                },
                'token': token
            }), 200)
            
            # 設置 Cookie
            response.set_cookie(
                'auth_token',
                token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=24 * 3600
            )
            
            return response
            
        except requests.RequestException as e:
            return jsonify({'message': f'Google 驗證失敗: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/oauth/apple', methods=['POST'])
def oauth_apple():
    """Apple Sign In 登入"""
    try:
        data = request.get_json()
        identity_token = data.get('identity_token')
        authorization_code = data.get('authorization_code')
        user_info = data.get('user', {})
        
        if not identity_token:
            return jsonify({'message': '缺少 Apple identity token'}), 400
        
        # 驗證 Apple token (簡化版 - 生產環境需要完整驗證)
        try:
            # 這裡應該驗證 Apple JWT token
            # 簡化處理：直接解析 token 獲取信息
            import base64
            
            # 解析 JWT token (不驗證簽名 - 僅用於開發)
            parts = identity_token.split('.')
            if len(parts) != 3:
                return jsonify({'message': '無效的 Apple token 格式'}), 401
            
            # 解碼 payload
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + '==').decode('utf-8'))
            
            # 提取用戶信息
            apple_id = payload.get('sub')
            email = user_info.get('email') or payload.get('email')
            
            if not apple_id:
                return jsonify({'message': '無法獲取 Apple 用戶 ID'}), 400
            
            # 查找或創建用戶
            user = None
            if email:
                user = User.get_by_email(email)
            
            if not user:
                # 創建新用戶
                username = f'apple_{apple_id[:8]}'
                # 確保用戶名唯一
                original_username = username
                counter = 1
                while User.get_by_username(username):
                    username = f'{original_username}_{counter}'
                    counter += 1
                
                # 使用隨機密碼
                random_password = secrets.token_urlsafe(32)
                hashed_password = hash_password(random_password)
                user = User.create(username, hashed_password, email)
            
            # 記錄登錄成功
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            User.record_login_success(user.username, ip_address, user_agent)
            
            # 生成 token
            token = generate_token(user.id, user.username, 24)
            
            # 保存 session
            expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
            User.save_session(user.id, token, ip_address, user_agent, expires_at)
            
            response = make_response(jsonify({
                'message': 'Apple 登入成功',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'isOAuth': True,
                    'oauthProvider': 'apple'
                },
                'token': token
            }), 200)
            
            # 設置 Cookie
            response.set_cookie(
                'auth_token',
                token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=24 * 3600
            )
            
            return response
            
        except Exception as e:
            return jsonify({'message': f'Apple 驗證失敗: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """忘記密碼 - 請求重置碼"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'message': '請輸入帳號'}), 400
        
        # 檢查用戶是否存在
        user = User.get_by_username(username)
        
        if not user:
            # 為了安全，即使用戶不存在也返回成功訊息
            return jsonify({'message': '如果帳號存在，重置碼已生成'}), 200
        
        # 生成重置 token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)  # 1小時後過期
        
        # 保存 token 到資料庫
        User.set_reset_token(username, token, expires_at)
        
        # 實際應用中，這裡應該發送郵件
        return jsonify({
            'message': '重置碼已生成',
            'token': token,
            'expires_at': expires_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """重置密碼"""
    try:
        data = request.get_json()
        username = data.get('username')
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not username or not token or not new_password:
            return jsonify({'message': '請填寫完整信息'}), 400
        
        # 驗證密碼長度
        if len(new_password) < 6:
            return jsonify({'message': '密碼長度至少需要6個字元'}), 400
        
        # 根據 token 查找用戶
        user = User.get_by_reset_token(token)
        
        if not user:
            return jsonify({'message': '無效的重置碼'}), 400
        
        # 驗證用戶名是否匹配
        if user.username != username:
            return jsonify({'message': '帳號與重置碼不匹配'}), 400
        
        # 檢查 token 是否過期
        if user.reset_token_expires:
            if isinstance(user.reset_token_expires, str):
                expires_at = datetime.fromisoformat(user.reset_token_expires.replace('Z', '+00:00'))
            else:
                expires_at = user.reset_token_expires
            
            if datetime.now() > expires_at:
                return jsonify({'message': '重置碼已過期，請重新申請'}), 400
        
        # 更新密碼（使用 bcrypt）
        hashed_password = hash_password(new_password)
        User.update_password(username, hashed_password)
        
        return jsonify({'message': '密碼重置成功'}), 200
        
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/user/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """獲取用戶資料"""
    try:
        user_id = request.current_user['user_id']
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({'message': '用戶不存在'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'last_login': user.last_login,
            'created_at': user.created_at
        }), 200
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/users', methods=['GET'])
@require_auth
def get_users():
    """獲取所有用戶列表（需要認證）"""
    try:
        users = User.get_all()
        # 不返回敏感信息
        return jsonify([{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'created_at': u.created_at
        } for u in users]), 200
    except Exception as e:
        return jsonify({'message': f'伺服器錯誤: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
