# Git 操作說明

## 已完成的 Git 初始化

### 1. 初始化 Git 倉庫
```bash
git init
```

### 2. 創建 .gitignore 檔案
已自動創建，排除以下檔案：
- macOS 系統檔案 (.DS_Store)
- 備份檔案 (*.bak, *~)
- 編輯器設定檔 (.vscode/, .idea/)
- 臨時檔案 (*.tmp, *.log)

### 3. 添加所有檔案
```bash
git add .
```

### 4. 提交檔案
```bash
git commit -m "Initial commit: 專題網頁介紹 - 具備情緒回饋與記憶紀錄的文字型 NPC 對話模擬系統"
```

**提交內容：**
- 14 個檔案
- 2307 行代碼
- 包含所有網頁檔案、樣式檔案、組員照片等

### 5. 連接遠端倉庫
```bash
git remote add origin https://github.com/linyouzi/npc.git
```

### 6. 設定分支名稱
```bash
git branch -M main
```

---

## 推送到 GitHub 的方法

### 方法 1：使用 GitHub CLI（推薦）

如果已安裝 GitHub CLI：
```bash
gh auth login
git push -u origin main
```

### 方法 2：使用個人存取令牌（Personal Access Token）

1. 前往 GitHub：https://github.com/settings/tokens
2. 點擊「Generate new token」→「Generate new token (classic)」
3. 設定名稱（例如：npc-project）
4. 勾選 `repo` 權限
5. 點擊「Generate token」
6. 複製產生的令牌

然後執行：
```bash
git remote set-url origin https://您的令牌@github.com/linyouzi/npc.git
git push -u origin main
```

### 方法 3：手動推送

在終端機執行：
```bash
cd "/Users/hclacree/Desktop/專題網頁介紹"
git push -u origin main
```

系統會提示輸入：
- GitHub 用戶名
- 密碼（或個人存取令牌）

---

## 後續操作

### 查看狀態
```bash
git status
```

### 查看遠端倉庫
```bash
git remote -v
```

### 添加新檔案並推送
```bash
git add .
git commit -m "更新說明"
git push
```

### 查看提交歷史
```bash
git log
```

---

## GitHub 倉庫資訊

- **倉庫 URL：** https://github.com/linyouzi/npc.git
- **分支：** main
- **狀態：** 已連接，待推送

---

## 注意事項

1. 推送前需要完成 GitHub 認證
2. 建議使用個人存取令牌而非密碼（更安全）
3. 首次推送後，後續更新只需執行 `git push` 即可
4. 所有檔案已提交到本地倉庫，隨時可以推送

---

**建立時間：** 2025年1月
**專題名稱：** 具備情緒回饋與記憶紀錄的文字型 NPC 對話模擬系統

