REFRESH_INTERVAL = 2

MIMO_URL = "https://platform.xiaomimimo.com/api/v1/tokenPlan/usage"
MIMO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Referer": "https://platform.xiaomimimo.com/console/plan-manage",
    "x-timezone": "Asia/Hong_Kong",
}
MIMO_COOKIE = (
    'cookie-preferences=%7B%22analytical%22%3Afalse%2C%22functional%22%3Afalse%7D; '
    'api-platform_serviceToken="yVHEDQlNiFT1WavLtPFnezgniFL7QG9QG6y5wnSX8tEQ6/HJ8F1s3gJPXPp6oUYCF+'
    'TFKeXpIyzRFVgx6Hzd97TF2Ui1ebZ1TXJiv1Q1v2aqhE2+gv7qDJ4qqcxe3evL1jVbDn2LL2hIIyMEUxbeFu0uF6fcJqWH2VU0ieTNkP+'
    'CzBXzuVhjSGSIsmts8nK86m2UYHQ7cI9vqKH+tPjjwlhXMtbftnKldkyZEcmrVaGw0iR59Sbi3dbVbcCA20uzIivjUGMNfZXYQY5CtBkkLZoa5VM5O7LjbOE3WmnrcPaRxxO2FzjqrpSV4uhwNUJT0VWx3HiqOCIq0sD3q3QeaNh+1leApDNequmMjohOv8g="; '
    'userId=1323241875; '
    'api-platform_slh="opRqhehpnBSbxhjkWfEj9iHfl3c="; '
    'api-platform_ph="vlyXfCB4KR6oi9fS+7U1uA=="'
)

DS_URL = "https://api.deepseek.com/user/balance"
DS_HEADERS = {
    "Accept": "application/json",
    "Authorization": "Bearer sk-03770f45145247698247b963a75945c0",
}

NO_PROXY = {"http": None, "https": None}
