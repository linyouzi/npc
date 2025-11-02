// 忘記密碼頁面邏輯
let resetToken = '';
let resetUsername = '';

// 顯示步驟
function showStep(stepNumber) {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById(`step${stepNumber}`).classList.add('active');
    document.getElementById('message').style.display = 'none';
}

// 請求重置碼
document.getElementById('requestResetForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('reset-username').value;
    const messageDiv = document.getElementById('message');
    
    try {
        const response = await fetch('http://localhost:5000/api/forgot-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resetToken = data.token;
            resetUsername = username;
            
            // 顯示重置碼
            document.getElementById('reset-token-display').textContent = resetToken;
            showStep(2);
        } else {
            messageDiv.className = 'message error';
            messageDiv.textContent = data.message || '請求失敗，請檢查帳號是否正確';
            messageDiv.style.display = 'block';
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '連接錯誤，請稍後再試';
        messageDiv.style.display = 'block';
        console.error('Error:', error);
    }
});

// 跳轉到重置密碼步驟
function goToResetStep() {
    document.getElementById('reset-username-final').value = resetUsername;
    showStep(3);
}

// 重置密碼
document.getElementById('resetPasswordForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('reset-username-final').value;
    const token = document.getElementById('reset-token').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const messageDiv = document.getElementById('message');
    
    // 驗證密碼是否一致
    if (newPassword !== confirmPassword) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '兩次輸入的密碼不一致';
        messageDiv.style.display = 'block';
        return;
    }
    
    // 驗證密碼長度
    if (newPassword.length < 6) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '密碼長度至少需要 6 個字元';
        messageDiv.style.display = 'block';
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/api/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                token,
                new_password: newPassword
            }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageDiv.className = 'message success';
            messageDiv.textContent = '密碼重置成功！即將跳轉到登錄頁面...';
            messageDiv.style.display = 'block';
            
            // 3 秒後跳轉到登錄頁面
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } else {
            messageDiv.className = 'message error';
            messageDiv.textContent = data.message || '重置失敗，請檢查重置碼是否正確或已過期';
            messageDiv.style.display = 'block';
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '連接錯誤，請稍後再試';
        messageDiv.style.display = 'block';
        console.error('Error:', error);
    }
});

