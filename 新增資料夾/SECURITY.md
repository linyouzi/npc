# 安全指南

## 生產環境部署建議

### 1. 環境變數設置
```bash
export SECRET_KEY="your-secret-key-here"
```

### 2. HTTPS 配置
- 必須啟用 HTTPS
- 更新 `backend/app.py` 中的 `secure=True` 設置

### 3. 資料庫安全
- 定期備份資料庫
- 使用強密碼保護資料庫文件
- 考慮使用 PostgreSQL 替代 SQLite（生產環境）

### 4. CORS 配置
- 限制允許的來源域名
- 不要使用 `CORS(app)`，應該指定具體域名

### 5. 速率限制
- 建議添加 API 速率限制（如 Flask-Limiter）
- 防止暴力破解和 DDoS 攻擊

### 6. 日誌和監控
- 監控異常登錄行為
- 設置告警通知
- 定期檢查登錄日誌

## 已實施的安全措施

1. ✅ 密碼 bcrypt 加密
2. ✅ JWT Token 認證
3. ✅ HTTP-only Cookies
4. ✅ 帳號鎖定機制
5. ✅ 登錄日誌記錄
6. ✅ Session 管理
7. ✅ Token 過期機制
8. ✅ 輸入驗證

## 待實施的安全措施（生產環境）

1. ⚠️ 雙因素認證（2FA）
2. ⚠️ 郵件驗證
3. ⚠️ API 速率限制
4. ⚠️ IP 白名單/黑名單
5. ⚠️ 密碼複雜度檢查
6. ⚠️ 定期強制更改密碼
7. ⚠️ 安全標頭（CSP, HSTS 等）

