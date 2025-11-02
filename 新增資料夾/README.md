# 具備情緒與記憶回饋的智能 NPC 互動系統

## 專案結構

```
project/
├── frontend/
│   ├── index.html          # 主頁面（包含「小夥伴」標題）
│   ├── login.html          # 登錄頁面
│   ├── forgot-password.html # 忘記密碼頁面
│   ├── dashboard.html      # 用戶控制台（登入後）
│   ├── npc.html            # 3D NPC 互動頁面
│   ├── auth.js             # 認證狀態管理
│   ├── script.js           # 前端邏輯
│   ├── npc-3d.js           # 3D NPC 渲染邏輯
│   └── styles.css          # 樣式文件
├── backend/
│   ├── app.py              # Flask 後端主程式
│   ├── auth.py             # 認證模組（JWT、密碼加密）
│   ├── models.py           # 資料模型
│   └── requirements.txt    # Python 依賴
└── database/
    └── users.db            # SQLite 資料庫（自動生成）
```

## 功能特色

### 🔐 專業登錄系統
- ✅ **JWT Token 認證**：使用 JWT 進行安全認證
- ✅ **bcrypt 密碼加密**：使用 bcrypt 進行密碼雜湊（兼容舊 SHA256）
- ✅ **Session 管理**：完整的 Session 追蹤和管理
- ✅ **帳號鎖定機制**：5次登錄失敗後鎖定30分鐘
- ✅ **登錄日誌記錄**：記錄所有登錄嘗試（成功/失敗）
- ✅ **「記住我」功能**：支持30天長期登錄
- ✅ **HTTP-only Cookies**：額外的安全保護層
- ✅ **路由保護**：需要認證才能訪問的頁面自動保護

### 📱 前端功能
- ✅ 主頁面：「小夥伴」以粗斜體顯示在正上方
- ✅ 登錄頁面：包含帳號密碼輸入框、登入按鈕、忘記密碼按鈕、「記住我」選項
- ✅ 用戶控制台：登入後的個人資料管理頁面
- ✅ 忘記密碼：完整的三步驟密碼重置流程
- ✅ 3D NPC 互動：使用 Three.js 顯示 3D NPC 模型

## 安裝與使用

### 1. 安裝後端依賴

```bash
cd backend
pip install -r requirements.txt
```

### 2. 啟動後端服務

```bash
python app.py
```

後端服務將運行在 `http://localhost:5000`

### 3. 開啟前端

直接用瀏覽器開啟 `frontend/login.html` 或 `frontend/index.html`

或使用本地伺服器：
```bash
cd frontend
python -m http.server 8000
```
然後訪問 `http://localhost:8000/login.html`

## API 端點

### 認證相關
- `POST /api/login` - 用戶登錄（返回 JWT token）
- `POST /api/logout` - 用戶登出（需認證）
- `GET /api/auth/verify` - 驗證當前認證狀態（需認證）
- `POST /api/register` - 用戶註冊
- `POST /api/forgot-password` - 申請密碼重置碼
- `POST /api/reset-password` - 重置密碼

### 用戶資料
- `GET /api/user/profile` - 獲取當前用戶資料（需認證）
- `GET /api/users` - 獲取所有用戶列表（需認證）

## 安全特性

- 🔒 **密碼加密**：使用 bcrypt（自動兼容舊 SHA256 密碼）
- 🔐 **JWT Token**：安全的認證 token，支持過期時間
- 🛡️ **帳號鎖定**：防止暴力破解攻擊
- 📝 **登錄日誌**：完整記錄所有登錄活動
- 🍪 **HTTP-only Cookies**：防止 XSS 攻擊
- 🔑 **Session 管理**：追蹤所有活躍 Session

## 資料庫結構

### users 表
- 用戶基本信息
- 密碼重置 token
- 登錄失敗次數和鎖定時間
- 最後登錄時間

### login_logs 表
- 所有登錄嘗試記錄
- IP 地址和 User Agent
- 成功/失敗狀態

### sessions 表
- 活躍 Session 追蹤
- Token 和過期時間
- IP 和設備信息

## 注意事項

- 資料庫會在首次運行時自動創建並遷移現有數據
- 舊密碼會自動兼容，新註冊用戶使用 bcrypt
- Token 預設24小時過期，「記住我」為30天
- 生產環境建議設置環境變數 `SECRET_KEY`
- 生產環境應啟用 HTTPS 並設置 `secure=True` 的 Cookies

