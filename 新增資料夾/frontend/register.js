// 註冊頁面邏輯
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const messageDiv = document.getElementById('message');
    
    messageDiv.style.display = 'none';
    
    // 驗證密碼是否一致
    if (password !== confirmPassword) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '兩次輸入的密碼不一致';
        messageDiv.style.display = 'block';
        return;
    }
    
    // 驗證用戶名長度
    if (username.length < 3 || username.length > 20) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '用戶名長度應在3-20個字元之間';
        messageDiv.style.display = 'block';
        return;
    }
    
    // 驗證密碼長度
    if (password.length < 6) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '密碼長度至少需要6個字元';
        messageDiv.style.display = 'block';
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                username,
                email: email || null,
                password
            }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageDiv.className = 'message success';
            messageDiv.textContent = '註冊成功！正在跳轉到登錄頁面...';
            messageDiv.style.display = 'block';
            
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);
        } else {
            messageDiv.className = 'message error';
            messageDiv.textContent = data.message || '註冊失敗，請稍後再試';
            messageDiv.style.display = 'block';
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '連接錯誤，請稍後再試';
        messageDiv.style.display = 'block';
        console.error('Error:', error);
    }
});

