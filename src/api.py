import requests
from dataclasses import dataclass
from config import MIMO_URL, MIMO_HEADERS, MIMO_COOKIE, DS_URL, DS_HEADERS, NO_PROXY
from settings import get as cfg


@dataclass
class MimoResult:
    ok: bool
    used: int = 0
    limit: int = 0
    percent: float = 0.0
    error: str = ""


@dataclass
class DeepseekResult:
    ok: bool
    is_available: bool = False
    total: float = 0.0
    granted: float = 0.0
    topped_up: float = 0.0
    error: str = ""


def query_mimo() -> MimoResult:
    try:
        cookie = cfg("mimo_cookie") or MIMO_COOKIE
        if not cookie:
            return MimoResult(ok=False, error="未配置 Cookie")
        headers = {**MIMO_HEADERS, "Cookie": cookie}
        resp = requests.get(MIMO_URL, headers=headers, timeout=10, proxies=NO_PROXY)
        data = resp.json()
        if data.get("code") == 0:
            usage = data["data"]["usage"]
            items = usage["items"]
            plan = next((i for i in items if i["name"] == "plan_total_token"), items[0])
            return MimoResult(ok=True, used=plan["used"], limit=plan["limit"], percent=usage["percent"])
        return MimoResult(ok=False, error=data.get("message", "未知错误"))
    except Exception as e:
        return MimoResult(ok=False, error=str(e)[:40])


def query_deepseek() -> DeepseekResult:
    try:
        api_key = cfg("ds_api_key") or DS_HEADERS["Authorization"].replace("Bearer ", "")
        headers = {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}
        resp = requests.get(DS_URL, headers=headers, timeout=10, proxies=NO_PROXY)
        data = resp.json()
        if "balance_infos" in data and data["balance_infos"]:
            info = data["balance_infos"][0]
            return DeepseekResult(
                ok=True, is_available=data.get("is_available", False),
                total=float(info["total_balance"]), granted=float(info["granted_balance"]),
                topped_up=float(info["topped_up_balance"]),
            )
        return DeepseekResult(ok=False, error="无余额数据")
    except Exception as e:
        return DeepseekResult(ok=False, error=str(e)[:40])
