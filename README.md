db.attendance_logs.createIndex({ employee_id: 1, type: 1 }, { unique: true })
db.attendance_daily.createIndex({ employee_id: 1, date: 1 }, { unique: true })
