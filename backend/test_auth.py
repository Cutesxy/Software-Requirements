"""
测试用户认证功能
"""
import auth
import requests
import json

def test_auth_module():
    """测试认证模块"""
    print("=" * 50)
    print("测试用户认证模块")
    print("=" * 50)
    
    # 初始化数据库
    print("\n1. 初始化数据库...")
    auth.init_db()
    auth.init_default_user()
    
    # 测试登录
    print("\n2. 测试登录功能...")
    success, message = auth.verify_user("admin", "123456")
    print(f"   登录 admin/123456: {success} - {message}")
    
    success, message = auth.verify_user("admin", "wrong_password")
    print(f"   登录 admin/wrong_password: {success} - {message}")
    
    # 测试创建用户
    print("\n3. 测试创建用户...")
    success, message = auth.create_user("testuser", "test123")
    print(f"   创建用户 testuser: {success} - {message}")
    
    # 测试获取用户信息
    print("\n4. 测试获取用户信息...")
    user_info = auth.get_user_info("admin")
    print(f"   用户信息: {user_info}")

def test_api_endpoints():
    """测试 API 端点（需要先启动服务器）"""
    base_url = "http://localhost:5319"
    
    print("\n" + "=" * 50)
    print("测试 API 端点")
    print("=" * 50)
    print("\n注意：请确保服务器已启动 (python api.py)")
    
    # 测试登录
    print("\n1. 测试登录接口...")
    try:
        response = requests.post(
            f"{base_url}/app/auth/login",
            json={"username": "admin", "password": "123456"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试检查登录状态
    print("\n2. 测试检查登录状态接口...")
    try:
        response = requests.get(f"{base_url}/app/auth/check")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"   错误: {e}")

if __name__ == "__main__":
    # 测试模块功能
    test_auth_module()
    
    # 测试 API（需要服务器运行）
    # test_api_endpoints()

