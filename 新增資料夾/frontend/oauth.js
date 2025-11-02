// OAuth 登入處理
let authManager;
if (typeof AuthManager !== 'undefined') {
    authManager = new AuthManager();
}

// Google 登入初始化
window.addEventListener('DOMContentLoaded', function() {
    // 綁定 Google 按鈕
    document.getElementById('google-signin-btn')?.addEventListener('click', () => {
        signInWithGoogle();
    });
    
    // 綁定 Apple 按鈕
    document.getElementById('apple-signin-btn')?.addEventListener('click', () => {
        signInWithApple();
    });
});

// Google 登入處理
async function signInWithGoogle() {
    try {
        // 簡化版：直接使用 Google Sign-In JavaScript API
        if (typeof google !== 'undefined' && google.accounts) {
            // 使用 Google Identity Services
            google.accounts.id.initialize({
                client_id: '', // 需要配置 Google OAuth Client ID
                callback: handleGoogleSignIn
            });
            
            // 顯示 One Tap 提示或彈出登入
            google.accounts.id.prompt();
            
            // 備用：顯示登入按鈕
            google.accounts.id.renderButton(
                document.getElementById('google-signin-btn'),
                { theme: 'outline', size: 'large', width: '100%' }
            );
        } else {
            // 如果 SDK 未載入，使用模擬方式（僅用於測試）
            showMessage('Google SDK 未載入，請檢查網絡連接或配置 Client ID', 'error');
        }
    } catch (error) {
        console.error('Google sign-in error:', error);
        showMessage('Google 登入功能需要配置 Client ID', 'error');
    }
}

function handleGoogleSignIn(response) {
    // Google 登入回調
    if (response.credential) {
        handleOAuthLogin('google', response.credential, null);
    }
}

// Apple 登入處理
async function signInWithApple() {
    try {
        if (typeof AppleID !== 'undefined') {
            // 初始化 Apple Sign In
            AppleID.auth.init({
                clientId: '', // 需要配置 Apple Client ID
                scope: 'name email',
                redirectURI: window.location.origin,
                usePopup: true
            });
            
            // 執行登入
            AppleID.auth.signIn({
                requestedScopes: ['email', 'name']
            }).then(async (response) => {
                // Apple 登入成功
                if (response.identity_token) {
                    await handleOAuthLogin('apple', response.identity_token, {
                        email: response.user?.email,
                        name: response.user?.name
                    });
                }
            }).catch((error) => {
                console.error('Apple sign-in error:', error);
                showMessage('Apple 登入失敗：請確保已配置 Apple Client ID', 'error');
            });
        } else {
            showMessage('Apple Sign In SDK 未載入，請檢查網絡連接或配置 Client ID', 'error');
        }
    } catch (error) {
        console.error('Apple sign-in error:', error);
        showMessage('Apple 登入功能需要配置 Client ID', 'error');
    }
}

// 統一處理 OAuth 登入
async function handleOAuthLogin(provider, token, userInfo) {
    const messageDiv = document.getElementById('message');
    messageDiv.style.display = 'none';
    
    try {
        let endpoint = '';
        let payload = {};
        
        if (provider === 'google') {
            endpoint = '/api/oauth/google';
            payload = { token: token };
        } else if (provider === 'apple') {
            endpoint = '/api/oauth/apple';
            payload = {
                identity_token: token,
                user: userInfo || {}
            };
        }
        
        const response = await fetch(`http://localhost:5000${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(payload),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 保存 token 和用戶數據
            if (data.token) {
                localStorage.setItem('auth_token', data.token);
                if (data.user) {
                    localStorage.setItem('user_data', JSON.stringify(data.user));
                }
            }
            
            messageDiv.className = 'message success';
            messageDiv.textContent = `${provider === 'google' ? 'Google' : 'Apple'} 登入成功！`;
            messageDiv.style.display = 'block';
            
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            messageDiv.className = 'message error';
            messageDiv.textContent = data.message || `${provider === 'google' ? 'Google' : 'Apple'} 登入失敗`;
            messageDiv.style.display = 'block';
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '連接錯誤，請稍後再試';
        messageDiv.style.display = 'block';
        console.error('OAuth login error:', error);
    }
}

// 顯示訊息
function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    messageDiv.style.display = 'block';
}

