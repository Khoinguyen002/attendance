from datetime import datetime, timezone

def today_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
