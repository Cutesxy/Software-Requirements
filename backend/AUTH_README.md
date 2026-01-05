# 用户登录系统使用说明

## 功能概述

基于 SQLite 数据库的简单用户登录系统，包含以下功能：
- 用户登录
- 用户注册
- 登录状态检查
- 用户登出

## 默认账号

系统会自动创建默认管理员账号：
- **用户名**: `admin`
- **密码**: `123456`

## 数据库

- 数据库文件位置: `backend/users.db`
- 首次运行时会自动创建数据库和用户表
- 默认账号会在首次运行时自动创建

## API 接口

### 1. 用户登录

**接口**: `POST /app/auth/login`

**请求体**:
```json
{
  "username": "admin",
  "password": "123456"
}
```

**成功响应** (200):
```json
{
  "success": true,
  "message": "登录成功",
  "user": {
    "id": 1,
    "username": "admin",
    "created_at": "2025-01-XX...",
    "last_login": "2025-01-XX..."
  }
}
```

**失败响应** (401):
```json
{
  "success": false,
  "message": "用户名或密码错误"
}
```

### 2. 用户注册

**接口**: `POST /app/auth/register`

**请求体**:
```json
{
  "username": "newuser",
  "password": "password123"
}
```

**成功响应** (200):
```json
{
  "success": true,
  "message": "用户创建成功"
}
```

**失败响应** (400):
```json
{
  "success": false,
  "message": "用户名已存在"  // 或其他错误信息
}
```

### 3. 检查登录状态

**接口**: `GET /app/auth/check`

**成功响应** (200):
```json
{
  "logged_in": true,
  "user": {
    "id": 1,
    "username": "admin",
    "created_at": "2025-01-XX...",
    "last_login": "2025-01-XX..."
  }
}
```

**未登录响应** (200):
```json
{
  "logged_in": false,
  "user": null
}
```

### 4. 用户登出

**接口**: `POST /app/auth/logout`

**成功响应** (200):
```json
{
  "success": true,
  "message": "登出成功"
}
```

## 使用示例

### Python 示例

```python
import requests

base_url = "http://localhost:5319"

# 登录
response = requests.post(
    f"{base_url}/app/auth/login",
    json={"username": "admin", "password": "123456"}
)
print(response.json())

# 检查登录状态
response = requests.get(f"{base_url}/app/auth/check")
print(response.json())

# 登出
response = requests.post(f"{base_url}/app/auth/logout")
print(response.json())
```

### JavaScript 示例

```javascript
const baseUrl = 'http://localhost:5319';

// 登录
fetch(`${baseUrl}/app/auth/login`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',  // 重要：包含 cookies
  body: JSON.stringify({
    username: 'admin',
    password: '123456'
  })
})
.then(res => res.json())
.then(data => console.log(data));

// 检查登录状态
fetch(`${baseUrl}/app/auth/check`, {
  credentials: 'include'
})
.then(res => res.json())
.then(data => console.log(data));
```

## 测试

运行测试脚本验证功能：

```bash
cd backend
python test_auth.py
```

## 注意事项

1. **会话管理**: 系统使用 Flask 的 session 来管理登录状态，前端请求时需要包含 cookies（`credentials: 'include'`）

2. **密码安全**: 密码使用 Werkzeug 的 `generate_password_hash` 进行加密存储

3. **生产环境**: 
   - 请修改 `api.py` 中的 `secret_key`
   - 考虑使用更安全的密码策略
   - 建议添加登录失败次数限制
   - 考虑使用 JWT 替代 session

4. **数据库**: SQLite 数据库文件 `users.db` 会在首次运行时自动创建

