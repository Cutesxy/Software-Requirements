"""
data_store.py - 拉取数据并保存到 MySQL 的主程序（使用 config.py 中的时间范围）
"""
from dateutil import parser
from datetime import timedelta
import config
from dbMapper import DBMapper

def main():
    db = DBMapper()
    db.init_db()
    print("Database initialized")
    # 从 config 中读取时间范围（字符串），并转为 datetime
    start_dt = parser.isoparse(config.START_DATE)
    end_dt = parser.isoparse(config.END_DATE)
    # 包含结束日全天
    end_dt = end_dt + timedelta(days=1)

    #TODO: Implement data fetching and storing logic


if __name__ == "__main__":
    main()