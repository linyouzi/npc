// 認證狀態管理模組
class AuthManager {
    constructor() {
        this.tokenKey = 'auth_token';
        this.userKey = 'user_data';
        this.apiBaseUrl = 'http://localhost:5000/api';
    }

    // 獲取 token
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    // 保存 token
    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }

    // 移除 token
    removeToken() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
    }

    // 獲取用戶數據
    getUser() {
        const userData = localStorage.getItem(this.userKey);
        return userData ? JSON.parse(userData) : null;
    }

    // 保存用戶數據
    setUser(user) {
        localStorage.setItem(this.userKey, JSON.stringify(user));
    }

    // 檢查是否已登錄
    isAuthenticated() {
        return !!this.getToken();
    }

    // 設置認證請求頭
    getAuthHeaders() {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };
    }

    // 登錄
    async login(username, password, rememberMe = false) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include', // 包含 cookies
                body: JSON.stringify({ username, password, remember_me: rememberMe })
            });

            const data = await response.json();

            if (response.ok) {
                this.setToken(data.token);
                this.setUser(data.user);
                return { success: true, data };
            } else {
                return { success: false, message: data.message || '登入失敗' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: '連接錯誤，請稍後再試' };
        }
    }

    // 登出
    async logout() {
        try {
            const token = this.getToken();
            if (token) {
                await fetch(`${this.apiBaseUrl}/logout`, {
                    method: 'POST',
                    headers: this.getAuthHeaders(),
                    credentials: 'include'
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.removeToken();
            window.location.href = 'login.html';
        }
    }

    // 驗證認證狀態
    async verifyAuth() {
        if (!this.isAuthenticated()) {
            return false;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/verify`, {
                method: 'GET',
                headers: this.getAuthHeaders(),
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                this.setUser(data.user);
                return true;
            } else {
                this.removeToken();
                return false;
            }
        } catch (error) {
            console.error('Verify auth error:', error);
            return false;
        }
    }

    // 保護路由（需要登錄才能訪問）
    async protectRoute() {
        const isAuth = await this.verifyAuth();
        if (!isAuth) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    }

    // 獲取用戶資料
    async getUserProfile() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/user/profile`, {
                method: 'GET',
                headers: this.getAuthHeaders(),
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                this.setUser(data);
                return { success: true, data };
            } else {
                return { success: false, message: '獲取資料失敗' };
            }
        } catch (error) {
            console.error('Get profile error:', error);
            return { success: false, message: '連接錯誤' };
        }
    }
}

// 創建全局實例
const authManager = new AuthManager();

