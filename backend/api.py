from flask import Flask, jsonify, request, session
from flask_cors import CORS
from datetime import datetime
import config
import service
import ai_service
import auth

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # 生产环境请更改此密钥
CORS(app, supports_credentials=True)

def _get_default_dates():
    """
    辅助函数：将 config 中的日期字符串转换为时间戳 (秒)
    Start: 当天 00:00:00
    End: 当天 23:59:59
    """
    try:
        start_dt = datetime.strptime(config.START_DATE, "%Y-%m-%d")
        end_dt = datetime.strptime(config.END_DATE, "%Y-%m-%d")
        # 设置结束时间为当天的最后一秒
        end_dt = end_dt.replace(hour=23, minute=59, second=59)
        return int(start_dt.timestamp()), int(end_dt.timestamp())
    except Exception as e:
        print(f"Config Date Parse Error: {e}")
        return 0, 0

@app.route("/app/getdata", methods=["GET"])
def getdata():
    """
    获取图表可视化数据
    Type: price | spread | heatmap | correlation
    Params: start, end, type, interval
    """
    try:
        default_start, default_end = _get_default_dates()
        
        # 1. 解析参数 (优先使用 URL 参数，否则使用 Config 转换后的时间戳)
        start = request.args.get('start', type=int)
        if start is None: start = default_start
            
        end = request.args.get('end', type=int)
        if end is None: end = default_end
            
        data_type = request.args.get('type', 'price')
        interval = request.args.get('interval', '15m')
        
        print(f"API Request: getdata type={data_type}, range={start}-{end}")

        # 2. 调用 service 层的函数
        if data_type == 'price':
            data = service.get_price_data(start, end, interval)
        elif data_type == 'spread':
            data = service.get_spread_data(start, end, interval)
        elif data_type == 'heatmap':
            data = service.get_heatmap_data(start, end)
        elif data_type == 'correlation':
            data = service.get_correlation_data(start, end)
        else:
            return jsonify({"error": "Unknown data type"}), 400

        return jsonify(data)

    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/app/getresult", methods=["GET"])
def getresult():
    """
    获取回测结果或信号
    Params: start, end, type, zThreshold, tradeSize
    """
    try:
        default_start, default_end = _get_default_dates()
        
        # 1. 解析时间
        start = request.args.get('start', type=int)
        if start is None: start = default_start
            
        end = request.args.get('end', type=int)
        if end is None: end = default_end
            
        res_type = request.args.get('type', 'backtest')
        
        # 2. 解析分析参数 (默认值来自 Config 的 ANALYSIS_PARAMS)
        # 注意: Config 中 trade_size_usdt 是 USDT 金额，这里作为 tradeSize 传入
        default_trade_size = config.ANALYSIS_PARAMS.get('trade_size_usdt', 10000)
        
        z_threshold = float(request.args.get('zThreshold', 2.0))
        trade_size = float(request.args.get('tradeSize', default_trade_size))
        
        print(f"API Request: getresult type={res_type}, size={trade_size}")
    
        # 3. 调用 service
        signals, backtest_stats = service.run_backtest(start, end, z_threshold, trade_size)

        if res_type == 'signals':
            return jsonify(signals)
        elif res_type == 'backtest':
            return jsonify(backtest_stats)
        else:
            return jsonify({"error": "Unknown result type"}), 400

    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/app/ai/chat", methods=["POST"])
def ai_chat():
    """
    AI 分析助手聊天接口
    Body: { "message": "用户消息", "context": {页面上下文} }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求体不能为空"}), 400
        
        message = data.get("message", "")
        context = data.get("context", {})
        
        if not message:
            return jsonify({"error": "消息不能为空"}), 400
        
        print(f"AI Chat Request: page={context.get('page', 'unknown')}, message={message[:50]}...")
        
        # 调用 AI 服务
        result = ai_service.chat_with_ai(message, context)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"AI Chat Error: {e}")
        return jsonify({
            "content": f"发生错误：{str(e)}",
            "functionCall": None
        }), 500

@app.route("/app/auth/login", methods=["POST"])
def login():
    """
    用户登录接口
    Body: { "username": "admin", "password": "123456" }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求体不能为空"}), 400
        
        username = data.get("username", "").strip()
        password = data.get("password", "")
        
        success, message = auth.verify_user(username, password)
        
        if success:
            # 设置会话
            session['username'] = username
            session['logged_in'] = True
            user_info = auth.get_user_info(username)
            return jsonify({
                "success": True,
                "message": message,
                "user": user_info
            })
        else:
            return jsonify({
                "success": False,
                "message": message
            }), 401
        
    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({
            "success": False,
            "message": f"登录失败: {str(e)}"
        }), 500

@app.route("/app/auth/logout", methods=["POST"])
def logout():
    """
    用户登出接口
    """
    try:
        session.clear()
        return jsonify({
            "success": True,
            "message": "登出成功"
        })
    except Exception as e:
        print(f"Logout Error: {e}")
        return jsonify({
            "success": False,
            "message": f"登出失败: {str(e)}"
        }), 500

@app.route("/app/auth/register", methods=["POST"])
def register():
    """
    用户注册接口
    Body: { "username": "newuser", "password": "password123" }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求体不能为空"}), 400
        
        username = data.get("username", "").strip()
        password = data.get("password", "")
        
        success, message = auth.create_user(username, password)
        
        if success:
            return jsonify({
                "success": True,
                "message": message
            })
        else:
            return jsonify({
                "success": False,
                "message": message
            }), 400
        
    except Exception as e:
        print(f"Register Error: {e}")
        return jsonify({
            "success": False,
            "message": f"注册失败: {str(e)}"
        }), 500

@app.route("/app/auth/check", methods=["GET"])
def check_auth():
    """
    检查当前登录状态
    """
    try:
        if session.get('logged_in') and session.get('username'):
            username = session.get('username')
            user_info = auth.get_user_info(username)
            return jsonify({
                "logged_in": True,
                "user": user_info
            })
        else:
            return jsonify({
                "logged_in": False,
                "user": None
            })
    except Exception as e:
        print(f"Check Auth Error: {e}")
        return jsonify({
            "logged_in": False,
            "user": None
        })

def main():
    # 初始化数据库和默认用户
    auth.init_db()
    auth.init_default_user()
    
    print(f"Starting Flask API on port {config.PORT}...")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)

if __name__ == "__main__":
    main()