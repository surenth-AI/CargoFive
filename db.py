import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
IS_POSTGRES = False

if DATABASE_URL and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")):
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        IS_POSTGRES = True
        print("Database Mode: PostgreSQL (Azure/Cloud)")
    except ImportError:
        print("WARNING: DATABASE_URL is set to PostgreSQL, but 'psycopg2-binary' is not installed.")
        print("Falling back to local SQLite database.")

def get_db_connection():
    if IS_POSTGRES:
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        # Enable connection timeout and keepalives for reliable cloud connections
        conn = psycopg2.connect(url, cursor_factory=RealDictCursor, connect_timeout=10)
        return conn
    else:
        conn = sqlite3.connect("app.db")
        conn.row_factory = sqlite3.Row
        return conn

def _execute(cursor, query, params=None):
    if IS_POSTGRES:
        # Translate SQLite ? placeholders to PostgreSQL %s placeholders
        query = query.replace('?', '%s')
    cursor.execute(query, params or ())
    return cursor

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
        # Create Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL CHECK(role IN ('employee', 'lead'))
            )
        """)
        
        # Create File Runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_runs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                filename VARCHAR(255) NOT NULL,
                start_time VARCHAR(100) NOT NULL,
                end_time VARCHAR(100),
                system_duration_sec INTEGER DEFAULT 0,
                manual_duration_sec INTEGER DEFAULT 0,
                status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create Issues / Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                category VARCHAR(100) NOT NULL,
                severity VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                performance_rating INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        # Create Users table (SQLite)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('employee', 'lead'))
            )
        """)
        
        # Create File Runs table (SQLite)
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

        # Create Issues / Feedback table (SQLite)
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
    _execute(cursor, "SELECT * FROM users WHERE username = 'lead'")
    if not cursor.fetchone():
        _execute(cursor, "INSERT INTO users (username, password, role) VALUES ('lead', 'password123', 'lead')")
        print("Default lead user created (username: 'lead', password: 'password123').")
        
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    _execute(cursor, "SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password, role="employee"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        _execute(cursor, "INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        err_str = str(e).lower()
        if "unique" in err_str or "duplicate" in err_str:
            return False
        print(f"Error creating user: {e}")
        return False

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    _execute(cursor, "SELECT id, username, role FROM users WHERE role = 'employee'")
    users = cursor.fetchall()
    conn.close()
    return users

def start_file_run(user_id, filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    start_time = datetime.now().isoformat()
    if IS_POSTGRES:
        _execute(cursor, """
            INSERT INTO file_runs (user_id, filename, start_time, status)
            VALUES (?, ?, ?, 'processing') RETURNING id
        """, (user_id, filename, start_time))
        row = cursor.fetchone()
        run_id = row['id'] if hasattr(row, 'keys') or isinstance(row, dict) else row[0]
    else:
        _execute(cursor, """
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
    _execute(cursor, """
        UPDATE file_runs
        SET end_time = ?, system_duration_sec = ?, status = 'completed'
        WHERE id = ?
    """, (end_time, system_duration_sec, run_id))
    conn.commit()
    conn.close()

def update_manual_time(run_id, manual_duration_sec):
    conn = get_db_connection()
    cursor = conn.cursor()
    _execute(cursor, """
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
    _execute(cursor, query, params)
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
    _execute(cursor, query, params)
    history = cursor.fetchall()
    conn.close()
    return [dict(row) for row in history]

def get_employee_kpis():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT u.username,
               COUNT(f.id) as total_files,
               SUM(f.system_duration_sec) as total_system_sec,
               SUM(f.manual_duration_sec) as total_manual_sec,
               ROUND(AVG(f.system_duration_sec), 2) as avg_system_sec,
               ROUND(AVG(f.manual_duration_sec), 2) as avg_manual_sec
        FROM users u
        LEFT JOIN file_runs f ON u.id = f.user_id AND f.status = 'completed'
        WHERE u.role = 'employee'
        GROUP BY u.id, u.username
    """
    _execute(cursor, query)
    kpis = cursor.fetchall()
    conn.close()
    return [dict(row) for row in kpis]

def log_issue(user_id, category, severity, title, description, performance_rating):
    conn = get_db_connection()
    cursor = conn.cursor()
    _execute(cursor, """
        INSERT INTO issues (user_id, category, severity, title, description, performance_rating)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, category, severity, title, description, performance_rating))
    conn.commit()
    conn.close()

def get_all_issues():
    conn = get_db_connection()
    cursor = conn.cursor()
    _execute(cursor, """
        SELECT i.id, u.username as employee, i.category, i.severity, i.title, i.description, 
               i.performance_rating, i.status, i.created_at
        FROM issues i
        JOIN users u ON i.user_id = u.id
        ORDER BY i.id DESC
    """)
    issues = cursor.fetchall()
    conn.close()
    return [dict(row) for row in issues]

try:
    init_db()
except Exception as e:
    print(f"Error during database initialization: {e}")


