#!/usr/bin/env python3
"""
PS5 光碟版主機 監控程式（PChome 24h、Yahoo購物中心、宏碁遊戲）
- 每隔 N 秒查一次，找到「光碟版主機、價格 <= 上限、目前可購買」就推播通知
- 只用 Python 標準函式庫，不用裝任何套件
- 通知管道：ntfy（手機 App 最簡單）、Telegram、Discord，填哪個就用哪個

用法：
    python3 ps5_monitor.py            # 持續監控
    python3 ps5_monitor.py --once     # 只查一次（測試用）
    python3 ps5_monitor.py --test-notify   # 送一則測試通知
"""

import json
import os
import re
import sys
import time
from html import unescape as html_unescape
import urllib.parse
import urllib.request
from datetime import datetime

# ====================== 設定區 ======================
MAX_PRICE = int(os.environ.get("MAX_PRICE", "22000"))            # 價格上限（含）
CHECK_INTERVAL = 60          # 幾秒查一次（建議 >= 60，別太頻繁）
KEYWORDS = ["PS5 光碟版", "PS5 主機 光碟", "PlayStation 5 光碟版"]
INCLUDE_BUNDLES = True       # True = 主機+遊戲同捆組也算；False = 只要單機

# --- 通知（不用的留空字串）---
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")              # 例如 "ps5-alert-你自己取個難猜的名字"，手機裝 ntfy App 訂閱同名 topic
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")      # 跟 @BotFather 申請
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")        # 跟 @userinfobot 查
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")         # Discord 頻道 → 整合 → Webhook

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ps5_state.json")
# ===================================================

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"}

# 名稱一定要像「主機」
MUST_ANY = ["主機", "CFI-2", "Slim"]
# 排除：數位版、Pro、周邊配件、二手
EXCLUDE = ["數位", "Digital", "Pro", "PRO", "光碟機", "保護", "收納", "包", "貼",
           "充電", "手把", "控制器 單", "支架", "直立架", "散熱", "硬碟", "SSD",
           "二手", "福利品", "Portal", "VR2", "耳機", "外殼", "面板", "防塵"]
BUNDLE_HINT = ["+", "＋", "同捆", "組", "《", "{"]


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def http_get_json(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", errors="replace")
    # PChome 部分 API 回傳 JSONP 格式，去掉外層
    m = re.match(r"^[^\[{]*?\((.*)\)\s*;?\s*$", raw, re.S)
    return json.loads(m.group(1) if m else raw)


def http_post(url, data: dict, as_json=False, timeout=15):
    if as_json:
        body = json.dumps(data).encode()
        headers = {**UA, "Content-Type": "application/json"}
    else:
        body = urllib.parse.urlencode(data).encode()
        headers = UA
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ---------------- PChome ----------------
def pchome_search(keyword, pages=2):
    prods = []
    for p in range(1, pages + 1):
        q = urllib.parse.quote(keyword)
        url = f"https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={q}&page={p}&sort=sale/dc"
        data = http_get_json(url)
        prods += data.get("prods") or []
        if p >= (data.get("totalPage") or 1):
            break
        time.sleep(1)
    return prods


def pchome_buyable(ids):
    """回傳 {商品Id: (是否可購買, 即時價格)}。查不到狀態時視為未知(None)。"""
    result = {}
    for i in range(0, len(ids), 20):
        chunk = ids[i:i + 20]
        url = ("https://ecapi-cdn.pchome.com.tw/ecshop/prodapi/v2/prod/button"
               f"&id={','.join(chunk)}&fields=Id,Price,ButtonType,SaleStatus,Qty")
        try:
            data = http_get_json(url)
        except Exception as e:
            log(f"庫存 API 失敗：{e}")
            continue
        for item in data if isinstance(data, list) else []:
            pid = re.sub(r"-\d{3}$", "", item.get("Id", ""))  # 去掉規格尾碼 -000
            btn = item.get("ButtonType", "")
            price = (item.get("Price") or {}).get("P") or (item.get("Price") or {}).get("M")
            result[pid] = (btn == "ForSale", price)
    return result


def is_target(name):
    if not any(k in name for k in MUST_ANY):
        return False
    if "光碟" not in name and not re.search(r"CFI-2\d{3}A", name):
        return False
    if any(k in name for k in EXCLUDE):
        return False
    if not INCLUDE_BUNDLES and any(k in name for k in BUNDLE_HINT):
        return False
    return True


def check_pchome():
    seen = {}
    for kw in KEYWORDS:
        try:
            for p in pchome_search(kw):
                if p.get("Id") and is_target(p.get("name", "")):
                    seen[p["Id"]] = p
        except Exception as e:
            log(f"PChome 搜尋「{kw}」失敗：{e}")
        time.sleep(1)

    candidates = {pid: p for pid, p in seen.items() if int(p.get("price") or 0) <= MAX_PRICE + 3000}
    status = pchome_buyable(list(candidates))

    hits = []
    for pid, p in candidates.items():
        ok, live_price = status.get(pid, (None, None))
        price = int(live_price or p.get("price") or 0)
        if ok and 0 < price <= MAX_PRICE:
            hits.append({
                "store": "PChome",
                "id": pid,
                "name": p["name"],
                "price": price,
                "url": f"https://24h.pchome.com.tw/prod/{pid}",
            })
    log(f"PChome：符合名稱 {len(seen)} 筆，可購買且 ≤ {MAX_PRICE} 共 {len(hits)} 筆")
    return hits


# ---------------- Yahoo購物中心 ----------------
def yahoo_search(keyword):
    q = urllib.parse.quote(keyword)
    req = urllib.request.Request(f"https://tw.buy.yahoo.com/search/product?p={q}&sort=rel",
                                 headers={**UA, "Accept-Language": "zh-TW,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=20) as r:
        page = r.read().decode("utf-8", errors="replace")
    i = page.find('"ecsearch":{"hits":')
    if i < 0:
        raise ValueError("找不到商品資料（Yahoo 頁面格式可能改了）")
    hits, _ = json.JSONDecoder().raw_decode(page, i + len('"ecsearch":{"hits":'))
    return hits


def check_yahoo():
    seen = {}
    for kw in KEYWORDS:
        try:
            for h in yahoo_search(kw):
                name = h.get("ec_title", "")
                if h.get("ec_productid") and is_target(name):
                    seen[h["ec_productid"]] = h
        except Exception as e:
            log(f"Yahoo 搜尋「{kw}」失敗：{e}")
        time.sleep(1)
    hits = []
    for pid, h in seen.items():
        price = int(float(h.get("ec_price") or 0))
        in_stock = h.get("ec_has_stock") == "1" and int(h.get("ec_stockcount") or 0) > 0
        if in_stock and 0 < price <= MAX_PRICE:
            hits.append({"store": "Yahoo", "id": pid, "name": h.get("ec_title", ""), "price": price,
                         "url": h.get("ec_item_url") or f"https://tw.buy.yahoo.com/gdsale/gdsale.asp?gdid={pid}"})
    log(f"Yahoo：符合名稱 {len(seen)} 筆，可購買且 ≤ {MAX_PRICE} 共 {len(hits)} 筆")
    return hits


# ---------------- 宏碁遊戲（PlayStation 台灣總代理）----------------
def _get_text(url, timeout=20):
    req = urllib.request.Request(url, headers={**UA, "Accept-Language": "zh-TW,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def check_acer():
    page = _get_text("https://www.acergaming.com/products/PS5")
    cards = re.split(r'class="productItem\b', page)[1:]
    seen = {}
    for c in cards:
        name = re.search(r'<h3 class="d-none">([^<]*)</h3>', c)
        link = re.search(r'href="(https://www\.acergaming\.com/product/detail/([^"?]+)[^"]*)"', c)
        price = re.search(r'data-price="([\d,]+)"', c)
        if not (name and link and price):
            continue
        n = html_unescape(name.group(1))
        if is_target(n):
            seen[link.group(2)] = {"name": n, "url": link.group(1), "price": int(price.group(1).replace(",", ""))}
    hits = []
    for pid, p in seen.items():
        if not (0 < p["price"] <= MAX_PRICE):
            continue
        try:
            d = _get_text(p["url"])
        except Exception as e:
            log(f"宏碁 商品頁失敗 {pid}：{e}")
            continue
        m = re.search(r"availability:\s*'([a-z_ ]+)'", d)
        status = m.group(1) if m else ""
        if status and status != "out_of_stock":
            hits.append({"store": "宏碁遊戲", "id": pid, "name": p["name"], "price": p["price"], "url": p["url"]})
        time.sleep(1)
    log(f"宏碁遊戲：符合名稱 {len(seen)} 筆，可購買且 ≤ {MAX_PRICE} 共 {len(hits)} 筆")
    return hits


# ---------------- 通知 ----------------
def notify(title, body, url=None):
    sent = False
    if NTFY_TOPIC:
        try:
            payload = {"topic": NTFY_TOPIC, "title": title, "message": body,
                       "priority": 5, "tags": ["video_game"]}
            if url:
                payload["click"] = url
            http_post("https://ntfy.sh/", payload, as_json=True)
            sent = True
        except Exception as e:
            log(f"ntfy 失敗：{e}")
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            http_post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                      {"chat_id": TELEGRAM_CHAT_ID, "text": f"{title}\n{body}\n{url or ''}"})
            sent = True
        except Exception as e:
            log(f"Telegram 失敗：{e}")
    if DISCORD_WEBHOOK:
        try:
            http_post(DISCORD_WEBHOOK, {"content": f"**{title}**\n{body}\n{url or ''}"}, as_json=True)
            sent = True
        except Exception as e:
            log(f"Discord 失敗：{e}")
    if not sent:
        log("⚠ 沒有設定任何通知管道，只印在畫面上")
    print(f"\a🔔 {title}\n{body}\n{url or ''}", flush=True)


# ---------------- 狀態（避免重複通知）----------------
def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def run_once(state):
    hits = []
    for checker in (check_pchome, check_yahoo, check_acer):
        try:
            hits += checker()
        except Exception as e:
            log(f"{checker.__name__} 錯誤：{e}")
    now_ids = set()
    for h in hits:
        key = f"{h['store']}:{h['id']}"
        now_ids.add(key)
        prev = state.get(key)
        # 新上架/補貨 → 通知；價格比上次通知時更低 → 再通知
        if prev is None or h["price"] < prev:
            tag = "補貨/新上架" if prev is None else f"降價（{prev}→{h['price']}）"
            notify(f"PS5 光碟版可購買！${h['price']:,}",
                   f"[{h['store']}] {tag}\n{h['name']}", h["url"])
        state[key] = h["price"]
    # 已售完/下架的移出，下次補貨才會再通知
    for key in list(state):
        if key not in now_ids:
            state.pop(key)
    save_state(state)


def main():
    if "--test-notify" in sys.argv:
        notify("PS5 監控測試", "收到這則代表通知設定 OK", "https://24h.pchome.com.tw/")
        return
    state = load_state()
    # --duration 秒數：跑這麼久就結束（給 GitHub Actions 用）
    duration = None
    if "--duration" in sys.argv:
        duration = int(sys.argv[sys.argv.index("--duration") + 1])
    start = time.time()
    log(f"開始監控：PS5 光碟版、≤ NT${MAX_PRICE:,}、每 {CHECK_INTERVAL} 秒")
    while True:
        try:
            run_once(state)
        except Exception as e:
            log(f"本輪錯誤：{e}")
        if "--once" in sys.argv:
            break
        if duration and time.time() - start + CHECK_INTERVAL > duration:
            break
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
