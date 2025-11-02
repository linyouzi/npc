# NVIDIA Omniverse 3D 模型整合指南

## 概述

本指南說明如何在 NVIDIA Omniverse 中創建 3D NPC 模型，並將其整合到智能 NPC 互動系統中。

## 第一步：安裝 NVIDIA Omniverse

1. 前往 [NVIDIA Omniverse 官網](https://www.nvidia.com/zh-tw/omniverse/)
2. 下載並安裝 **Omniverse Launcher**
3. 在 Launcher 中安裝 **Omniverse Create**（用於場景構建和模型創作）

## 第二步：在 Omniverse 中創建 NPC 模型

### 方法一：使用內建模型庫
1. 打開 Omniverse Create
2. 在 Content 面板中瀏覽內建的角色模型
3. 選擇適合的 NPC 角色
4. 可以調整顏色、大小、姿勢等

### 方法二：匯入現有模型
1. 使用 Omniverse 連接器將模型從其他軟體（如 Blender、Maya）匯入
2. 或直接將 GLB/GLTF 格式的模型拖拽到場景中

### 方法三：從頭創建
1. 使用 Omniverse 的建模工具創建基礎形狀
2. 添加材質和紋理
3. 設置骨骼和動畫（可選）

## 第三步：設置動畫（可選）

如果需要 NPC 有動作：
1. 在 Timeline 面板中創建動畫
2. 設置關鍵幀
3. 可以添加：
   - 走路動畫
   - 說話動畫（口型同步）
   - 手勢動畫
   - 情緒表達動畫

## 第四步：導出模型

### 導出為 GLB/GLTF 格式（推薦）

1. 在 Omniverse Create 中選擇你的 NPC 模型
2. 點擊 **File** > **Export** > **Export Selected**
3. 選擇格式：**glTF Binary (.glb)** 或 **glTF (.gltf)**
4. 保存位置：專案的 `frontend/models/` 資料夾
5. 命名為 `npc.glb`

### 導出設定建議：
- ✅ 包含紋理和材質
- ✅ 包含動畫（如果有的話）
- ✅ 優化網格（減少面數以提升網頁性能）
- ✅ 設置適當的縮放比例

## 第五步：整合到專案中

### 1. 創建 models 資料夾
```bash
mkdir frontend/models
```

### 2. 放置模型文件
將從 Omniverse 導出的 `npc.glb` 文件放到 `frontend/models/` 資料夾中

### 3. 測試載入
1. 開啟 `frontend/npc.html`
2. 確認模型能正常載入和顯示
3. 測試動畫和互動功能

## 進階功能：整合情緒與記憶系統

### 情緒表達
在 Omniverse 中創建不同情緒的動畫變體：
- `idle_happy.glb` - 開心情緒
- `idle_sad.glb` - 難過情緒
- `idle_neutral.glb` - 中性情緒

然後在 `npc-3d.js` 中根據 AI 回饋的情緒載入對應的模型或動畫。

### 記憶系統整合
可以根據對話歷史改變 NPC 的：
- 表情
- 姿勢
- 手勢
- 場景中的位置

## 技術細節

### 支援的格式
- ✅ **GLB** (glTF Binary) - 推薦，單一文件包含所有資源
- ✅ **GLTF** (glTF JSON) - 需要額外的資源文件
- ⚠️ **USD** - Omniverse 原生格式，需要轉換為 GLB/GLTF 才能在網頁中使用

### 性能優化建議
1. **減少多邊形數量**：網頁版建議 5000-10000 個三角形
2. **壓縮紋理**：使用 WebP 或壓縮的 PNG/JPG
3. **LOD（細節層次）**：為遠距離創建低細節版本
4. **動畫優化**：只保留必要的動畫軌道

### 瀏覽器相容性
- Chrome/Edge：✅ 完全支援
- Firefox：✅ 完全支援
- Safari：✅ 完全支援（iOS 13+）

## 常見問題

### Q: 模型載入失敗？
A: 檢查：
- 文件路徑是否正確（`models/npc.glb`）
- 文件格式是否為 GLB/GLTF
- 瀏覽器控制台是否有錯誤訊息

### Q: 模型太大或太小？
A: 在 `npc-3d.js` 中調整 `npcModel.scale.set(x, y, z)` 的值

### Q: 動畫不播放？
A: 確認：
- 模型導出時包含動畫
- `mixer` 對象已正確初始化
- `isAnimating` 設為 true

### Q: 如何添加多個 NPC？
A: 可以載入多個模型實例，或創建包含多個角色的場景文件

## 參考資源

- [NVIDIA Omniverse 官方文件](https://docs.omniverse.nvidia.com/)
- [Three.js GLTFLoader 文檔](https://threejs.org/docs/#examples/en/loaders/GLTFLoader)
- [glTF 格式規格](https://www.khronos.org/gltf/)

## 下一步

1. 在 Omniverse 中創建或選擇 NPC 模型
2. 導出為 GLB 格式
3. 放置到 `frontend/models/` 資料夾
4. 測試並調整模型大小和位置
5. 整合情緒和記憶系統功能

