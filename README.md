# YouTube AI Agent 影音知識庫自動化建構指南 (Agent SOP & Workflow Blueprint)

> 本專案為 **YouTube 頻道影音知識庫自動化建構專案**。本份說明文件專為 **人類開發者** 與 **自主 AI Agent（如 Claude Code, OpenAI Codex, Google AntiGravity, OpenCode 等）** 設計。  
> **所有 Agent 必須先遵守 [AGENTS.md](AGENTS.md) 的角色、Writer Lock、branch／PR 與人工合併規則，再依此指南處理知識庫。**

---

## 🤖 給 AI Agent 的執行指令 (Agent System Prompt / SOP)

如果你是一個正在接手或維護此專案的 AI Agent，請嚴格遵循以下協議進行操作：

1. **環境檢查**：確認執行環境中具備 Python 3.10+、`yt-dlp`（最新版）與 `ffmpeg`。若套件版本過舊，優先升級 `yt-dlp`。
2. **網路存取**：抓取 YouTube 頻道 API 與字幕需具備網路連線權限（若在沙盒環境請依工具權限流程取得必要網路權限，不得自行繞過安全限制）。
3. **分層結構**：
   - 主索引檔統一為 `AI_Agent_影片清單.md`，必須按主題分類與集數（`EP01~`）由小到大排序。
   - 所有逐字稿統一儲存在 `字幕/<分類資料夾>/` 下，檔名需進行檔案系統特殊字元清理（`sanitize_filename`）。
4. **逐字稿清理規範**：
   - 移除 WebVTT/SRT 的樣式標籤（如 `<c>`, `<00:00:01>` 等）。
   - 過濾 YouTube 自動字幕常見的相鄰重複字句。
   - 依語意停頓與時間間隔（建議 30~45 秒）進行段落聚合，並前綴 `[HH:MM:SS]` 時間錨點。
5. **雙向超連結**：完成逐字稿轉換後，必須將檔案相對路徑填回主索引清單，形成可點擊跳轉的知識網絡。

---

## 📌 專案架構概覽 (Repository Architecture)

```text
.
├── README.md                 # 專案總覽與 Agent 執行標準作業程序 (SOP)
├── build_knowledge_base.py   # 一鍵式自動化爬取、分類、下載與轉檔 Python 腳本
├── AI_Agent_影片清單.md       # 知識庫主索引清單（含集數排序、影片連結、字幕檔跳轉）
└── 字幕/                     # 逐字稿 Markdown 儲存目錄
    ├── 01_Google_AntiGravity/# Google AntiGravity 實測、備課、GAS、Skill 系列
    ├── 02_Claude_Code/       # Claude 生態、Skills、Obsidian、Supabase、Remote Control 系列
    ├── 03_GPT_Codex/         # GPT-CodeX 安裝初始化、第二大腦、資料庫串接、實戰系列
    ├── 04_OpenCode/          # OpenCode 開源 Agent、Token 解放、開源模型搭配系列
    └── 05_AI_Agent/          # AI Agent 核心基本功、需求四象限、MCP 連接器、跨電腦協作
```

---

## ⚙️ 前置需求與環境準備 (Prerequisites)

在執行建構前，請確保終端具備以下工具：

```bash
# 1. 檢查 Python 版本 (需 3.10 以上)
python3 --version

# 2. 安裝或升級 yt-dlp 至最新穩定版本
python3 -m pip install --upgrade yt-dlp

# 3. (選用) 檢查 ffmpeg (用於音訊多媒體處理)
which ffmpeg || brew install ffmpeg
```

---

## 🚀 一鍵快速建構 (Quick Start)

本專案已封裝完整的一鍵式建構腳本 [`build_knowledge_base.py`](file:///Users/wuruiqing/Library/CloudStorage/GoogleDrive-rangching0331@gmail.com/我的雲端硬碟/Agent專用/build_knowledge_base.py)。

只需在終端執行以下指令：

```bash
python3 build_knowledge_base.py
```

腳本將自動依序執行：
1. 爬取 `@sensebar` 頻道所有影片、直播與短影音元資料。
2. 進行關鍵字過濾與 5 大核心領域分類。
3. 啟動多執行緒（4 Workers）批次下載並清洗字幕為 Markdown。
4. 動態生成主索引檔 [`AI_Agent_影片清單.md`](file:///Users/wuruiqing/Library/CloudStorage/GoogleDrive-rangching0331@gmail.com/我的雲端硬碟/Agent專用/AI_Agent_影片清單.md)。

---

## 🛠️ 核心工作流程解析 (Step-by-Step Workflow)

若 Agent 需手動或分階段客製化執行，請依據以下標準 5 步驟：

### 步驟 1：頻道元資料扁平化抓取 (Flat Extraction)
使用 `yt-dlp` 的 `extract_flat: True` 與 `--no-check-certificate`，在不下載實體影片的前提下，快速取得頻道內所有影片的 `id`、`title` 與 `url`：
```python
import yt_dlp

ydl_opts = {
    'extract_flat': True,
    'nocheckcertificate': True,
    'quiet': True,
    'skip_download': True,
}
# 抓取包含 /videos, /streams, /shorts
```

### 步驟 2：語意分類與集數正則解析 (Categorization & Sorting)
1. **分類維度**：
   - `Google AntiGravity`：包含 `antigravity`, `anti gravity`。
   - `Claude / Claude Code`：包含 `claude` 且排除單純提及 Codex 的比較片。
   - `GPT Codex`：包含 `codex`, `gpt-codex`。
   - `OpenCode`：包含 `opencode`, `open code`。
   - `AI Agent 總覽與實戰`：包含 `agent`, `代理`, `智能體` 及跨工具綜合應用。
2. **集數解析**：
   - 使用正規表達式匹配 `r'ep\s*(\d+)'` 與小數點集數（如 `EP095` -> `EP 09.5`），轉換為浮點數後進行升冪排序。

### 步驟 3：智慧字幕提取 (Smart Subtitle Fetching)
1. **語言偏好排序**：`['zh-TW', 'zh-Hant', 'zh', 'en']`。
2. **自動字幕備援**：同時開啟 `writesubtitles` 與 `writeautomaticsub`。
3. **格式指定**：統一提取 `vtt` 格式，以取得原始毫秒級時間戳記。
4. **多執行緒併發控制**：使用 `ThreadPoolExecutor(max_workers=4)`，既能保證在 1 分鐘內下載近百部字幕，又可避免觸發 YouTube 429 請求頻率限制。

### 步驟 4：WebVTT 清理與 Markdown 轉換 (Transcript Processing)
1. **移除標籤**：透過 `re.sub(r'<[^>]+>', '', text)` 去除所有樣式標籤。
2. **消除重複行**：自動比對前後句，剔除 YouTube 自動字幕因滾動刷新而造成的文字重複。
3. **時間區間聚合**：將原本零碎的 1~2 秒字幕行，聚合為約 30~45 秒的語意段落，並標記 `[HH:MM:SS]`，大幅提升閱讀體驗與 LLM 檢索精確度。

### 步驟 5：動態關聯主索引 (Index Linking)
將產出的 Markdown 字幕檔案路徑填入 [`AI_Agent_影片清單.md`](file:///Users/wuruiqing/Library/CloudStorage/GoogleDrive-rangching0331@gmail.com/我的雲端硬碟/Agent專用/AI_Agent_影片清單.md)：
- 成功抓取者：生成可點擊相對連結（例如：`[查看字幕](字幕/02_Claude_Code/....md)`）。
- 直播或無字幕者：標記為 `⚠️ 無字幕（直播未提供）`，維持知識庫資訊透明度。

---

## ⚠️ 常見問題與除錯機制 (Troubleshooting)

| 問題現象 | 原因分析 | 解決策略 |
| :--- | :--- | :--- |
| `SSL: CERTIFICATE_VERIFY_FAILED` | macOS 本機 Python 證書未安裝或沙盒環境阻擋 | 在 `yt_dlp` 參數中設定 `'nocheckcertificate': True`，或執行 macOS 的 `Install Certificates.command`。 |
| `HTTP Error 403: Forbidden` | YouTube 針對部分已結束直播存檔（Live Stream Replay）限制未驗證訪客下載 | 直播存檔若無公開字幕，程式將自動捕獲並標註 `無字幕`，不中斷整體批次流程。 |
| 檔名過長或包含特殊字元導致存檔失敗 | 影片標題常含有 `|`, `/`, `:`, `?` 等非法字元 | 執行 `sanitize_filename()` 正則替換非法字元為底線 `_`，並限制檔名長度在 100 字元以內。 |
| 字幕大量跳字或重複斷詞 | YouTube 自動字幕機制導致同一詞句反覆出現 | 轉換器採用「相鄰字句去重」+「45 秒語意聚合」演算法，產出自然連貫的文章段落。 |

---

## 📄 授權與宣告 (License & Disclaimer)

本專案程式碼與建構流程採 [MIT License](LICENSE) 開源授權。逐字稿與影片內容之著作權均屬原頻道創作者 [三師爸 @sensebar](https://www.youtube.com/@sensebar) 所有，本工具僅供教育研習、學術研究與個人 AI 輔助學習使用。

## Multi-Agent Software Engineering Stack

共用規範：[AGENTS.md](AGENTS.md)；角色與交接：[MULTI_AGENT_WORKFLOW](docs/MULTI_AGENT_WORKFLOW.md)；環境、CI 與 GitHub 設定：[DEVELOPMENT](docs/DEVELOPMENT.md)；架構：[ARCHITECTURE](docs/ARCHITECTURE.md)。

正式修改一律 branch + PR，以 GitHub Actions 實際結果驗證，獨立 review 後由人類批准及合併。
