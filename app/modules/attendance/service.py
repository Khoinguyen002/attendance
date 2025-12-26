from datetime import datetime, timezone
from bson import ObjectId

from app.extensions.mongo import mongo
from app.modules.attendance.utils import today_str
from app.modules.attendance.rules import evaluate_attendance
from pymongo.errors import DuplicateKeyError

def scan_attendance(employee_id: str):
    employee_oid = ObjectId(employee_id)
    today = today_str()
    now = datetime.now(timezone.utc)

    daily = mongo.db.attendance_daily.find_one({
        "employee_id": employee_oid,
        "date": today
    })

    # ===== CHECK-IN =====
    if not daily:
        try:
            mongo.db.attendance_logs.insert_one({
                "employee_id": employee_oid,
                "type": "check_in",
                "timestamp": now
            })
            mongo.db.attendance_daily.insert_one({
                "employee_id": employee_oid,
                "date": today,
                "check_in": now,
                "check_out": None,
            })
        except DuplicateKeyError:
            raise ValueError("Already checked in today")


        return "check_in"

    # ⛔ ĐÃ CHECK-OUT
    if daily.get("check_out"):
        raise ValueError("Already checked out today")

    # ===== CHECK-OUT =====
    try:
        mongo.db.attendance_logs.insert_one({
            "employee_id": employee_oid,
            "type": "check_out",
            "timestamp": now
        })
    except DuplicateKeyError:
        raise ValueError("Already checked out today")


    # ===== APPLY RULE =====

    rule_result = evaluate_attendance(daily)

    result = mongo.db.attendance_daily.update_one(
        {"_id": daily["_id"], "check_out": None},
        {"$set": rule_result}
    )
    
    
    if result.matched_count == 0:
        raise ValueError("Already checked out")

    return "check_out"
