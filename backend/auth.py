"""
用户认证模块 - 使用 SQLite 数据库管理用户登录
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    """初始化数据库，创建用户表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")

def init_default_user():
    """初始化默认账号 admin/123456"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查是否已存在 admin 用户
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone():
        print("默认账号 admin 已存在，跳过创建")
        conn.close()
        return
    
    # 创建默认账号
    password_hash = generate_password_hash('123456')
    created_at = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO users (username, password_hash, created_at)
        VALUES (?, ?, ?)
    ''', ('admin', password_hash, created_at))
    
    conn.commit()
    conn.close()
    print("默认账号 admin/123456 创建成功")

def verify_user(username, password):
    """
    验证用户登录
    返回: (success: bool, message: str)
    """
    if not username or not password:
        return False, "用户名和密码不能为空"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询用户
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False, "用户名或密码错误"
    
    password_hash = result[0]
    
    # 验证密码
    if check_password_hash(password_hash, password):
        # 更新最后登录时间
        cursor.execute('''
            UPDATE users SET last_login = ? WHERE username = ?
        ''', (datetime.now().isoformat(), username))
        conn.commit()
        conn.close()
        return True, "登录成功"
    else:
        conn.close()
        return False, "用户名或密码错误"

def create_user(username, password):
    """
    创建新用户
    返回: (success: bool, message: str)
    """
    if not username or not password:
        return False, "用户名和密码不能为空"
    
    if len(username) < 3:
        return False, "用户名至少需要3个字符"
    
    if len(password) < 6:
        return False, "密码至少需要6个字符"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查用户名是否已存在
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return False, "用户名已存在"
    
    # 创建新用户
    password_hash = generate_password_hash(password)
    created_at = datetime.now().isoformat()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, created_at)
            VALUES (?, ?, ?)
        ''', (username, password_hash, created_at))
        conn.commit()
        conn.close()
        return True, "用户创建成功"
    except Exception as e:
        conn.close()
        return False, f"创建用户失败: {str(e)}"

def get_user_info(username):
    """获取用户信息"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, created_at, last_login
        FROM users WHERE username = ?
    ''', (username,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'username': result[1],
            'created_at': result[2],
            'last_login': result[3]
        }
    return None

# 初始化数据库和默认用户
if __name__ == "__main__":
    init_db()
    init_default_user()
    print("用户认证模块初始化完成")

