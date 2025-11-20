# Backend API for Uniswap V3 vs Binance USDT/ETH Analysis

概览:
- get_data.py  : 获取数据主函数，负责从 The Graph (Uniswap V3) 与 Binance 拉取数据
- dbMapper.py    : DBMapper 类，负责 MySQL 连接、表结构与增删查改
- analysis.py : Analyzer 类，实现非原子套利事件识别与收益估算
- api.py         : Flask REST API（JSON），前端使用 JS 调用这些接口
- config.py      : 配置文件
- test_db.py     :数据库连接测试文件(AI生成的，有问题自己麻烦改一下)
- requirements.txt: Python 依赖

快速启动:
1. 修改 config.py 中 MYSQL_URI 与 POOL_ADDRESS。
2. 安装依赖: pip install -r requirements.txt
3. 运行：python get_data.py
4. 运行: python api.py
5. API:
   - GET  /app/getdata      -> 返回数据库中交易
   - GET  /app/getresult    -> 返回分析结果

后端还需要完成的部分：
- get_data.py
- analysis.py
- api.py