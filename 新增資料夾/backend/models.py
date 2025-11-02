import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'users.db')

class User:
    def __init__(self, id, username, password, email=None, reset_token=None, reset_token_expires=None, 
                 failed_login_attempts=0, locked_until=None, last_login=None, created_at=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.reset_token = reset_token
        self.reset_token_expires = reset_token_expires
        self.failed_login_attempts = failed_login_attempts or 0
        self.locked_until = locked_until
        self.last_login = last_login
        self.created_at = created_at
    
    @staticmethod
    def init_db():
        """初始化資料庫"""
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                reset_token TEXT,
                reset_token_expires TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 為現有表添加新欄位（如果不存在）
        columns_to_add = [
            ('reset_token', 'TEXT'),
            ('reset_token_expires', 'TIMESTAMP'),
            ('email', 'TEXT'),
            ('failed_login_attempts', 'INTEGER DEFAULT 0'),
            ('locked_until', 'TIMESTAMP'),
            ('last_login', 'TIMESTAMP')
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
            except sqlite3.OperationalError:
                pass  # 欄位已存在
        
        # 創建登錄日誌表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 創建 Session 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def create(username, password, email=None):
        """創建新用戶"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
            (username, password, email)
        )
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return User(user_id, username, password, email)
    
    @staticmethod
    def get_by_username(username):
        """根據用戶名獲取用戶"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password, email, reset_token, reset_token_expires, 
                   failed_login_attempts, locked_until, last_login, created_at 
            FROM users WHERE username = ?
        ''', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
        return None
    
    @staticmethod
    def get_by_email(email):
        """根據電子郵件獲取用戶"""
        if not email:
            return None
            
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password, email, reset_token, reset_token_expires, 
                   failed_login_attempts, locked_until, last_login, created_at 
            FROM users WHERE email = ?
        ''', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
        return None
    
    @staticmethod
    def get_by_id(user_id):
        """根據 ID 獲取用戶"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password, email, reset_token, reset_token_expires, 
                   failed_login_attempts, locked_until, last_login, created_at 
            FROM users WHERE id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
        return None
    
    @staticmethod
    def update_password(username, new_password):
        """更新用戶密碼"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE users SET password = ?, reset_token = NULL, reset_token_expires = NULL, failed_login_attempts = 0, locked_until = NULL WHERE username = ?',
            (new_password, username)
        )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def record_login_success(username, ip_address=None, user_agent=None):
        """記錄登錄成功"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        user = User.get_by_username(username)
        if user:
            # 更新最後登錄時間和重置失敗次數
            cursor.execute(
                'UPDATE users SET last_login = ?, failed_login_attempts = 0, locked_until = NULL WHERE username = ?',
                (datetime.now().isoformat(), username)
            )
            
            # 記錄登錄日誌
            cursor.execute(
                'INSERT INTO login_logs (user_id, username, ip_address, user_agent, success) VALUES (?, ?, ?, ?, ?)',
                (user.id, username, ip_address, user_agent, True)
            )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def record_login_failure(username, ip_address=None, user_agent=None):
        """記錄登錄失敗"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        user = User.get_by_username(username)
        if user:
            # 增加失敗次數
            failed_attempts = (user.failed_login_attempts or 0) + 1
            locked_until = None
            
            # 如果失敗5次以上，鎖定帳號30分鐘
            if failed_attempts >= 5:
                from datetime import timedelta
                locked_until = (datetime.now() + timedelta(minutes=30)).isoformat()
            
            cursor.execute(
                'UPDATE users SET failed_login_attempts = ?, locked_until = ? WHERE username = ?',
                (failed_attempts, locked_until, username)
            )
            
            # 記錄登錄日誌
            cursor.execute(
                'INSERT INTO login_logs (user_id, username, ip_address, user_agent, success) VALUES (?, ?, ?, ?, ?)',
                (user.id, username, ip_address, user_agent, False)
            )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def is_locked(username):
        """檢查帳號是否被鎖定"""
        user = User.get_by_username(username)
        if not user or not user.locked_until:
            return False
        
        try:
            locked_until = datetime.fromisoformat(user.locked_until.replace('Z', '+00:00'))
            if datetime.now() < locked_until:
                return True
            else:
                # 解鎖帳號
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE users SET locked_until = NULL, failed_login_attempts = 0 WHERE username = ?',
                    (username,)
                )
                conn.commit()
                conn.close()
                return False
        except:
            return False
    
    @staticmethod
    def set_reset_token(username, token, expires_at):
        """設置密碼重置 token"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 將 datetime 轉換為字串格式存儲
        expires_str = expires_at.isoformat() if hasattr(expires_at, 'isoformat') else str(expires_at)
        cursor.execute(
            'UPDATE users SET reset_token = ?, reset_token_expires = ? WHERE username = ?',
            (token, expires_str, username)
        )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_by_reset_token(token):
        """根據重置 token 獲取用戶"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, username, password, reset_token, reset_token_expires FROM users WHERE reset_token = ?',
            (token,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(row[0], row[1], row[2], row[3], row[4])
        return None
    
    @staticmethod
    def get_all():
        """獲取所有用戶"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password, email, reset_token, reset_token_expires, 
                   failed_login_attempts, locked_until, last_login, created_at 
            FROM users
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        return [User(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]) for row in rows]
    
    @staticmethod
    def save_session(user_id, token, ip_address=None, user_agent=None, expires_at=None):
        """保存 Session"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO sessions (user_id, token, ip_address, user_agent, expires_at) VALUES (?, ?, ?, ?, ?)',
            (user_id, token, ip_address, user_agent, expires_at)
        )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_session(token):
        """刪除 Session"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_session_by_token(token):
        """根據 token 獲取 Session"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, token, expires_at FROM sessions WHERE token = ?', (token,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # 檢查是否過期
            if row[2]:
                try:
                    expires_at = datetime.fromisoformat(row[2].replace('Z', '+00:00'))
                    if datetime.now() > expires_at:
                        User.delete_session(token)
                        return None
                except:
                    pass
            return {'user_id': row[0], 'token': row[1]}
        return None

