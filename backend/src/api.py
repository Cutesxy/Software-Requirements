"""
api.py - Flask API 服务主程序

Routes:
- GET  /app/getdata      -> 返回数据库中交易
- GET  /app/getresult    -> 返回分析结果
"""

from flask import Flask, jsonify
import config

from dbMapper import DBMapper
from analysis import Analyzer

app = Flask(__name__)

# 初始化
db = DBMapper()
db.init_db()
print("Database initialized")
analyzer = Analyzer(db)
@app.route("/app/getdata", methods=["GET"])
def getdata():

    #TODO: Implement data retrieval logic

    print("Received /app/getdata request")
    return jsonify(message="getdata response")

@app.route("/app/getresult", methods=["GET"])
def getresult():

    #TODO: Implement result retrieval logic

    print("Received /app/getresult request")
    return jsonify(message="getresult response")

def main(host="127.0.0.1", port=5000, debug=True):
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()