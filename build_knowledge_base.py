"""
YouTube AI Agent 知識庫自動化建構腳本 (build_knowledge_base.py)
功能：
1. 自動抓取指定 YouTube 頻道的所有影片清單。
2. 針對目標關鍵字（如 AntiGravity, Claude, Codex, OpenCode, AI Agent）進行智慧分類與集數排序。
3. 批次下載字幕（優先繁體中文，支援自動字幕），清理 WebVTT 重複贅詞並轉為結構化 Markdown。
4. 自動產出總覽索引清單 (AI_Agent_影片清單.md) 與字幕資料夾。
"""

import os
import re
import json
import glob
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import yt_dlp

# --- 設定參數 ---
CHANNEL_URL = 'https://www.youtube.com/@sensebar'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUB_DIR = os.path.join(BASE_DIR, '字幕')
INDEX_FILE = os.path.join(BASE_DIR, 'AI_Agent_影片清單.md')
TEMP_DIR = os.path.join(BASE_DIR, '.temp_cache')

CATEGORIES = [
    ("01_Google_AntiGravity", "一、 Google AntiGravity 系列", lambda t: 'antigravity' in t or 'anti gravity' in t),
    ("02_Claude_Code", "二、 Claude / Claude Code 系列", lambda t: 'claude' in t and 'codex' not in t),
    ("03_GPT_Codex", "三、 GPT Codex 系列", lambda t: 'gpt-codex' in t or 'gptcodex' in t or 'codex 基本功' in t or ('codex' in t and 'claude' not in t)),
    ("04_OpenCode", "四、 OpenCode 系列", lambda t: 'opencode' in t or 'open code' in t),
    ("05_AI_Agent", "五、 AI Agent 核心概念與多工具協作實戰", lambda t: ('agent' in t or '代理' in t or 'codex' in t or 'claude' in t) and not ('房仲' in t or '保險' in t)),
]

def sanitize_filename(name):
    clean = re.sub(r'[\\/*?:"<>|]', '_', name)
    clean = re.sub(r'\s+', '_', clean)
    clean = clean.strip(' ._')
    return clean[:100]

def parse_ep(title):
    m_dec = re.search(r'ep\s*095', title.lower())
    if m_dec:
        return 9.5, "EP 09.5"
    m = re.search(r'ep\s*(\d+)', title.lower())
    if m:
        num = int(m.group(1))
        return float(num), f"EP {num:02d}"
    return 999.0, "專題影片"

def fetch_channel_videos():
    print(f"[*] 正在抓取頻道影片清單: {CHANNEL_URL}")
    os.makedirs(TEMP_DIR, exist_ok=True)
    ydl_opts = {
        'extract_flat': True,
        'nocheckcertificate': True,
        'quiet': True,
        'skip_download': True,
    }
    urls = [
        f"{CHANNEL_URL}/videos",
        f"{CHANNEL_URL}/streams",
        f"{CHANNEL_URL}/shorts",
    ]
    all_videos = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for u in urls:
            try:
                res = ydl.extract_info(u, download=False)
                for e in res.get('entries', []):
                    if e and e.get('id'):
                        vid = e['id']
                        if vid not in all_videos:
                            all_videos[vid] = {
                                'id': vid,
                                'title': e.get('title', ''),
                                'url': e.get('url') or f"https://www.youtube.com/watch?v={vid}"
                            }
            except Exception as err:
                print(f"[!] 抓取 {u} 時發生錯誤: {err}")
    
    videos_list = list(all_videos.values())
    print(f"[+] 成功獲取 {len(videos_list)} 部影片")
    return videos_list

def vtt_to_markdown(vtt_path, title, url, vid, cat):
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    cues = []
    current_time = None
    current_text = []

    time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[\.,]\d{3})')

    for line in lines:
        line = line.strip()
        if not line or line.startswith(('WEBVTT', 'Kind:', 'Language:', 'NOTE')):
            continue

        m = time_pattern.search(line)
        if m:
            if current_time and current_text:
                text = ' '.join(current_text).strip()
                if text:
                    cues.append((current_time, text))
            current_time = m.group(1)[:8]
            current_text = []
        else:
            cleaned = re.sub(r'<[^>]+>', '', line).strip()
            if cleaned and (not current_text or current_text[-1] != cleaned):
                current_text.append(cleaned)

    if current_time and current_text:
        text = ' '.join(current_text).strip()
        if text:
            cues.append((current_time, text))

    def to_sec(ts):
        p = ts.split(':')
        return int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])

    grouped = []
    last_sec = -999
    current_group_time = ""
    current_group_lines = []

    for ts, txt in cues:
        sec = to_sec(ts)
        if sec - last_sec >= 45:
            if current_group_lines:
                grouped.append((current_group_time, "".join(current_group_lines)))
            current_group_time = ts
            current_group_lines = [txt]
            last_sec = sec
        else:
            if current_group_lines and current_group_lines[-1] == txt:
                continue
            current_group_lines.append(txt)

    if current_group_lines:
        grouped.append((current_group_time, "".join(current_group_lines)))

    md = [
        f"# {title}\n",
        f"- **原始影片連結**：[{url}]({url})",
        f"- **影片 ID**：`{vid}`",
        f"- **所屬分類**：`{cat}`\n",
        "---\n",
        "## 字幕逐字稿\n"
    ]

    for ts, text in grouped:
        md.append(f"**[{ts}]** {text}\n")

    return "\n".join(md)

def download_and_convert_sub(task):
    vid = task['id']
    cat = task['cat']
    title = task['title']
    url = task['url']

    clean_name = sanitize_filename(title)
    target_md_name = f"{clean_name}.md"
    target_md_path = os.path.join(SUB_DIR, cat, target_md_name)
    rel_md_path = f"字幕/{cat}/{target_md_name}"

    if os.path.exists(target_md_path) and os.path.getsize(target_md_path) > 100:
        return {'id': vid, 'status': 'success', 'path': rel_md_path}

    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['zh-TW', 'zh-Hant', 'zh', 'en'],
        'subtitlesformat': 'vtt',
        'outtmpl': os.path.join(TEMP_DIR, f"{vid}.%(ext)s"),
        'nocheckcertificate': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception:
        pass

    vtts = glob.glob(os.path.join(TEMP_DIR, f"{vid}*.vtt"))
    if not vtts:
        return {'id': vid, 'status': 'no_sub', 'path': rel_md_path}

    best_vtt = vtts[0]
    for pref in ['.zh-TW.', '.zh-Hant.', '.zh.', '.en.']:
        for f in vtts:
            if pref in f:
                best_vtt = f
                break

    try:
        md_text = vtt_to_markdown(best_vtt, title, url, vid, cat)
        with open(target_md_path, 'w', encoding='utf-8') as f:
            f.write(md_text)
        for f in vtts:
            try: os.remove(f)
            except: pass
        return {'id': vid, 'status': 'success', 'path': rel_md_path}
    except Exception as e:
        return {'id': vid, 'status': 'error', 'error': str(e), 'path': rel_md_path}

def main():
    videos = fetch_channel_videos()
    os.makedirs(SUB_DIR, exist_ok=True)
    for cat_dir, _, _ in CATEGORIES:
        os.makedirs(os.path.join(SUB_DIR, cat_dir), exist_ok=True)

    # 歸類影片
    tasks = []
    seen_vids = set()
    category_map = {}

    for cat_dir, cat_name, filter_fn in CATEGORIES:
        category_map[cat_dir] = []
        for v in videos:
            t = v['title'].lower()
            if filter_fn(t):
                if v['id'] not in seen_vids:
                    seen_vids.add(v['id'])
                    task = {
                        'cat': cat_dir,
                        'id': v['id'],
                        'title': v['title'],
                        'url': v['url']
                    }
                    tasks.append(task)
                    category_map[cat_dir].append(task)

    print(f"[*] 符合篩選條件的獨立影片共：{len(tasks)} 部")
    print("[*] 開始多執行緒下載與轉換字幕 (4 workers)...")

    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(download_and_convert_sub, t): t for t in tasks}
        count = 0
        for f in as_completed(futures):
            res = f.result()
            results[res['id']] = res
            count += 1
            if count % 10 == 0 or count == len(tasks):
                print(f"    進度: {count}/{len(tasks)}")

    # 產出 Markdown 總覽索引
    print("[*] 正在產生 AI_Agent_影片清單.md...")
    md_lines = [
        "# 三師爸 (@sensebar) AI Agent 系列影片清單整理\n",
        "> 本清單由自動化知識庫建構腳本生成，專注於 **AI Agent**、**Google AntiGravity**、**Claude / Claude Code**、**GPT Codex**、**OpenCode** 等系列影片。\n",
        "每個系列均依照 **集數（EP01～）** 進行排序，方便循序漸進學習。\n\n---\n"
    ]

    for cat_dir, cat_name, _ in CATEGORIES:
        items = category_map.get(cat_dir, [])
        # 排序
        formatted_items = []
        for t in items:
            num, ep_str = parse_ep(t['title'])
            formatted_items.append((num, ep_str, t))
        formatted_items.sort(key=lambda x: (x[0], x[2]['title']))

        md_lines.append(f"## {cat_name}\n")
        md_lines.append("| 集數 / 標籤 | 影片標題 | 影片連結 | 字幕逐字稿 (MD) |")
        md_lines.append("| :--- | :--- | :--- | :--- |")

        for _, ep_str, t in formatted_items:
            clean_t = t['title'].replace('|', '｜').strip()
            vid = t['id']
            u = t['url']
            res = results.get(vid, {})
            if res.get('status') == 'success':
                sub_link = f"[{os.path.basename(res['path'])}]({res['path']})"
            else:
                sub_link = "⚠️ 無字幕（直播未提供）"
            md_lines.append(f"| {ep_str} | {clean_t} | [前往觀看]({u}) | {sub_link} |")
        md_lines.append("\n")

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))

    print(f"[+] 知識庫建構完成！主索引位於: {INDEX_FILE}")

if __name__ == '__main__':
    main()
