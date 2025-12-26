from datetime import datetime, time, timezone
import pytz

from app.config import Config


TZ = pytz.timezone(Config.TIMEZONE)


def _parse_time(value: str) -> time:
    h, m = value.split(":")
    return time(int(h), int(m))


WORK_START = _parse_time(Config.WORK_START)
WORK_END = _parse_time(Config.WORK_END)

def calc_penalty_days(total_minutes: int) -> float:
    if total_minutes < 10:
        return 0.0
    elif total_minutes <= 20:
        return 0.25
    elif total_minutes <= 40:
        return 0.5
    elif total_minutes <= 65:
        return 1.0
    else:
        return 1.0


def evaluate_attendance(daily: dict) -> dict:
    """
    Input: attendance_daily record
    Output: {
        status: full | late | early | late_early | absent,
        late_minutes: int,
        early_minutes: int,
        penalty_days: float
    }
    """
    now = datetime.now(timezone.utc)
    
    if not daily.get("check_in"):
        return {
            "status": "absent",
            "late_minutes": 0,
            "early_minutes": 0,
            "penalty_days": 1.0  
        }

    check_in = daily["check_in"].replace(tzinfo=timezone.utc).astimezone(TZ)
    check_out = now.astimezone(TZ)

    start_dt = TZ.localize(
        datetime.combine(
            check_in.date(), WORK_START
        )
    )

    end_dt = TZ.localize(
        datetime.combine(
            check_in.date(), WORK_END
        )
    )
    
    late_minutes = max(
        int((check_in - start_dt).total_seconds() / 60), 0
    )

    early_minutes = max(
        int((end_dt - check_out).total_seconds() / 60), 0
    )

    # status
    if late_minutes > 0 and early_minutes > 0:
        status = "late_early"
    elif late_minutes > 0:
        status = "late"
    elif early_minutes > 0:
        status = "early"
    else:
        status = "full"

    total_violation_minutes = late_minutes + early_minutes
    penalty_days = calc_penalty_days(total_violation_minutes)

    return {
        "status": status,
        "check_out": now,
        "late_minutes": late_minutes,
        "early_minutes": early_minutes,
        "penalty_days": penalty_days
    }
