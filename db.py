import sqlite3
import os
from datetime import datetime

DB_PATH = "app.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('employee', 'lead'))
        )
    """)
    
    # Create File Runs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            system_duration_sec INTEGER DEFAULT 0,
            manual_duration_sec INTEGER DEFAULT 0,
            status TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Create Issues / Feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            performance_rating INTEGER NOT NULL,
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Create default Lead/Admin user if it doesn't exist
    cursor.execute("SELECT * FROM users WHERE username = 'lead'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('lead', 'password123', 'lead')")
        print("Default lead user created (username: 'lead', password: 'password123').")
        
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password, role="employee"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.UniqueViolationError:
        return False
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE role = 'employee'")
    users = cursor.fetchall()
    conn.close()
    return users

def start_file_run(user_id, filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    start_time = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO file_runs (user_id, filename, start_time, status)
        VALUES (?, ?, ?, 'processing')
    """, (user_id, filename, start_time))
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id

def complete_file_run(run_id, system_duration_sec):
    conn = get_db_connection()
    cursor = conn.cursor()
    end_time = datetime.now().isoformat()
    cursor.execute("""
        UPDATE file_runs
        SET end_time = ?, system_duration_sec = ?, status = 'completed'
        WHERE id = ?
    """, (end_time, system_duration_sec, run_id))
    conn.commit()
    conn.close()

def update_manual_time(run_id, manual_duration_sec):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE file_runs
        SET manual_duration_sec = ?
        WHERE id = ?
    """, (manual_duration_sec, run_id))
    conn.commit()
    conn.close()

def get_user_history(user_id, from_date=None, to_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT id, filename, start_time, end_time, system_duration_sec, manual_duration_sec, status, created_at
        FROM file_runs
        WHERE user_id = ?
    """
    params = [user_id]
    if from_date:
        query += " AND created_at >= ?"
        params.append(from_date)
    if to_date:
        query += " AND created_at <= ?"
        params.append(to_date)
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    history = cursor.fetchall()
    conn.close()
    return [dict(row) for row in history]

def get_lead_history(from_date=None, to_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT f.id, u.username as employee, f.filename, f.start_time, f.end_time, 
               f.system_duration_sec, f.manual_duration_sec, f.status, f.created_at
        FROM file_runs f
        JOIN users u ON f.user_id = u.id
    """
    params = []
    conditions = []
    if from_date:
        conditions.append("f.created_at >= ?")
        params.append(from_date)
    if to_date:
        conditions.append("f.created_at <= ?")
        params.append(to_date)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY f.id DESC"
    cursor.execute(query, params)
    history = cursor.fetchall()
    conn.close()
    return [dict(row) for row in history]

def get_employee_kpis():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username,
               COUNT(f.id) as total_files,
               SUM(f.system_duration_sec) as total_system_sec,
               SUM(f.manual_duration_sec) as total_manual_sec,
               ROUND(AVG(f.system_duration_sec), 2) as avg_system_sec,
               ROUND(AVG(f.manual_duration_sec), 2) as avg_manual_sec
        FROM users u
        LEFT JOIN file_runs f ON u.id = f.user_id AND f.status = 'completed'
        WHERE u.role = 'employee'
        GROUP BY u.id
    """)
    kpis = cursor.fetchall()
    conn.close()
    return [dict(row) for row in kpis]

def log_issue(user_id, category, severity, title, description, performance_rating):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO issues (user_id, category, severity, title, description, performance_rating)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, category, severity, title, description, performance_rating))
    conn.commit()
    conn.close()

def get_all_issues():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, u.username as employee, i.category, i.severity, i.title, i.description, 
               i.performance_rating, i.status, i.created_at
        FROM issues i
        JOIN users u ON i.user_id = u.id
        ORDER BY i.id DESC
    """)
    issues = cursor.fetchall()
    conn.close()
    return [dict(row) for row in issues]

init_db()

