import sqlite3

conn = sqlite3.connect("hostel.db")
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# STUDENTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_no TEXT UNIQUE,
    name TEXT NOT NULL,
    gender TEXT,
    course TEXT,
    year TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    room_no TEXT,
    guardian_name TEXT,
    guardian_phone TEXT,
    admission_date TEXT
)
""")

# ROOMS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_no TEXT UNIQUE,
    room_type TEXT,
    capacity INTEGER,
    occupied INTEGER DEFAULT 0,
    status TEXT
)
""")

# ROOM ALLOCATION TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS room_allocation(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_no TEXT,
    room_no TEXT,
    allocation_date TEXT
)
""")

# ATTENDANCE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_no TEXT,
    date TEXT,
    status TEXT
)
""")

# FEES TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS fees(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_no TEXT,
    total_fee REAL,
    paid_fee REAL,
    balance_fee REAL,
    payment_date TEXT,
    payment_mode TEXT
)
""")

# COMPLAINTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS complaints(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_no TEXT,
    complaint TEXT,
    complaint_date TEXT,
    status TEXT
)
""")

# VISITORS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS visitors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visitor_name TEXT,
    student_enrollment TEXT,
    relation TEXT,
    phone TEXT,
    visit_date TEXT,
    in_time TEXT,
    out_time TEXT
)
""")

# NOTICES TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS notices(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    notice_date TEXT
)
""")

# ID CARDS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS idcards(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_no TEXT,
    issue_date TEXT
)
""")
# Insert default users
users = [
    ("admin", "admin123", "Admin"),
    ("warden", "warden123", "Warden"),
    ("accountant", "account123", "Accountant"),
    ("student", "student123", "Student")
]

for user in users:
    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, role)
    VALUES (?, ?, ?)
    """, user)
    
conn.commit()
conn.close()

print("All tables created successfully!")