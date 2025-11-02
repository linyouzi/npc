# OAuth 登入設置指南

## Google 登入設置

### 1. 創建 Google OAuth 憑證

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新專案或選擇現有專案
3. 啟用 **Google+ API**
4. 前往「憑證」>「建立憑證」>「OAuth 客戶端 ID」
5. 應用程式類型選擇「網頁應用程式」
6. 授權的 JavaScript 來源：`http://localhost:5000` (開發環境)
7. 授權的重新導向 URI：`http://localhost:5000/oauth-callback.html`
8. 複製 **Client ID**

### 2. 配置前端

在 `frontend/oauth.js` 中更新：
```javascript
google.accounts.id.initialize({
    client_id: 'YOUR_GOOGLE_CLIENT_ID_HERE',
    callback: handleGoogleSignIn
});
```

## Apple 登入設置

### 1. 創建 Apple 開發者帳號

1. 前往 [Apple Developer Portal](https://developer.apple.com/)
2. 創建 App ID
3. 在「功能」中啟用「Sign in with Apple」
4. 創建 Service ID
5. 配置「Sign in with Apple」
6. 下載私鑰文件

### 2. 配置前端

在 `frontend/oauth.js` 中更新：
```javascript
AppleID.auth.init({
    clientId: 'YOUR_APPLE_CLIENT_ID_HERE',
    scope: 'name email',
    redirectURI: window.location.origin,
    usePopup: true
});
```

## 測試模式

目前系統已實現基本框架，但在沒有配置 Client ID 的情況下：

- **Google 登入**：會顯示錯誤提示，需要配置 Client ID
- **Apple 登入**：會顯示錯誤提示，需要配置 Client ID

## 開發環境測試

如果暫時無法配置 OAuth，可以：

1. 使用「訪客登入」功能測試系統
2. 使用傳統的帳號密碼登入
3. 配置測試用的 OAuth Client ID

## 生產環境部署

部署到生產環境時：

1. 更新 OAuth Client ID 為生產環境的值
2. 更新授權的重定向 URI
3. 確保使用 HTTPS
4. 配置正確的域名和回調 URL

## 注意事項

- OAuth 功能需要有效的 Client ID 才能正常運作
- Google 和 Apple 都需要在各自的開發者平台完成設置
- 生產環境必須使用 HTTPS
- 確保後端 API 正確處理 OAuth token 驗證

