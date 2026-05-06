REFRESH_INTERVAL = 2

MIMO_URL = "https://platform.xiaomimimo.com/api/v1/tokenPlan/usage"
MIMO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Referer": "https://platform.xiaomimimo.com/console/plan-manage",
    "x-timezone": "Asia/Hong_Kong",
}
MIMO_COOKIE = ""  # 在设置面板中填入你的 Cookie

DS_URL = "https://api.deepseek.com/user/balance"
DS_HEADERS = {
    "Accept": "application/json",
    "Authorization": "Bearer YOUR_API_KEY",  # 在设置面板中填入你的 API Key
}

NO_PROXY = {"http": None, "https": None}
