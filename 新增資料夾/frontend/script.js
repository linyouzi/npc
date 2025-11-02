// 載入認證管理器
let authManager;
if (typeof AuthManager !== 'undefined') {
    authManager = new AuthManager();
} else {
    // 如果 auth.js 未載入，使用舊版方式
    console.warn('AuthManager not loaded, using fallback');
}

// 訪客登入
async function loginAsGuest() {
    const messageDiv = document.getElementById('message');
    messageDiv.style.display = 'none';
    
    try {
        // 生成訪客帳號
        const guestUsername = 'guest_' + Date.now();
        const guestPassword = 'guest_' + Math.random().toString(36).substring(7);
        
        // 先註冊訪客帳號
        const registerResponse = await fetch('http://localhost:5000/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                username: guestUsername,
                password: guestPassword
            }),
        });
        
        if (registerResponse.ok || registerResponse.status === 400) {
            // 如果註冊失敗（可能是帳號已存在），嘗試登入
            const loginResponse = await fetch('http://localhost:5000/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    username: guestUsername,
                    password: guestPassword,
                    remember_me: false
                }),
            });
            
            const loginData = await loginResponse.json();
            
            if (loginResponse.ok) {
                if (loginData.token) {
                    localStorage.setItem('auth_token', loginData.token);
                    if (loginData.user) {
                        localStorage.setItem('user_data', JSON.stringify({
                            ...loginData.user,
                            isGuest: true
                        }));
                    }
                }
                messageDiv.className = 'message success';
                messageDiv.textContent = '訪客登入成功！';
                messageDiv.style.display = 'block';
                
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 500);
            } else {
                // 如果登入也失敗，使用 API 的訪客登入
                const guestResponse = await fetch('http://localhost:5000/api/guest-login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include'
                });
                
                const guestData = await guestResponse.json();
                
                if (guestResponse.ok) {
                    if (guestData.token) {
                        localStorage.setItem('auth_token', guestData.token);
                        if (guestData.user) {
                            localStorage.setItem('user_data', JSON.stringify({
                                ...guestData.user,
                                isGuest: true
                            }));
                        }
                    }
                    messageDiv.className = 'message success';
                    messageDiv.textContent = '訪客登入成功！';
                    messageDiv.style.display = 'block';
                    
                    setTimeout(() => {
                        window.location.href = 'dashboard.html';
                    }, 500);
                } else {
                    throw new Error(guestData.message || '訪客登入失敗');
                }
            }
        } else {
            throw new Error('訪客註冊失敗');
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '訪客登入失敗，請稍後再試';
        messageDiv.style.display = 'block';
        console.error('Guest login error:', error);
    }
}

// 登錄表單處理
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('remember-me')?.checked || false;
    const messageDiv = document.getElementById('message');
    
    messageDiv.style.display = 'none';
    
    // 使用認證管理器（如果可用）
    if (authManager) {
        const result = await authManager.login(username, password, rememberMe);
        
        if (result.success) {
            messageDiv.className = 'message success';
            messageDiv.textContent = '登入成功！正在跳轉...';
            messageDiv.style.display = 'block';
            
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            messageDiv.className = 'message error';
            messageDiv.textContent = result.message || '登入失敗，請檢查帳號密碼';
            messageDiv.style.display = 'block';
        }
    } else {
        // 備用方案
        try {
            const response = await fetch('http://localhost:5000/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ username, password, remember_me: rememberMe }),
            });
            
            const data = await response.json();
            
            if (response.ok) {
                if (data.token) {
                    localStorage.setItem('auth_token', data.token);
                    if (data.user) {
                        localStorage.setItem('user_data', JSON.stringify(data.user));
                    }
                }
                messageDiv.className = 'message success';
                messageDiv.textContent = '登入成功！';
                messageDiv.style.display = 'block';
                
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            } else {
                messageDiv.className = 'message error';
                messageDiv.textContent = data.message || '登入失敗，請檢查帳號密碼';
                messageDiv.style.display = 'block';
            }
        } catch (error) {
            messageDiv.className = 'message error';
            messageDiv.textContent = '連接錯誤，請稍後再試';
            messageDiv.style.display = 'block';
            console.error('Error:', error);
        }
    }
});

