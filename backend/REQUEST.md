# 区块链非原子套利交易识别
## 项目背景
交易者利用去中心化交易所（DEX）和中心化交易所（CEX）之间同一代币的价格差，执行非原
子套利（Non-Atomic Arbitrage）来获得利润。与原子套利不同，非原子套利的交易不是在一
个区块或一笔交易中完成的，因此存在一定的风险，比如价格变化或交易延迟。
本项目以 Uniswap V3 和 Binance 之间的 USDT/ETH 交易对为研究对象，通过对两边的价格
数据进行分析，尝试识别其中可能存在的非原子套利行为。
## 需求
实现一个Web应用，完成如下两个核心功能:
1. 展示 2025 年 9 月 1 日至 9 月 30 日期间，Ethereum上Uniswap V3（USDT/ETH池）与
Binance（USDT/ETH 交易对）的历史成交数据，并对两者价格变化进行可视化对比。
2. 对 Uniswap V3与Binance之间的USDT/ETH交易数据进行分析，探索并实现识别非原子套
利行为的方法，可结合启发式规则、统计分析或其他可行手段，计算潜在获利金额（以
USDT 为单位）。
## 数据来源：
1. 对Uniswap V3上其中一个USDT/ETH池进行分析
❑ 以太坊合约地址： 0x11b815efB8f581194ae79006d24E0d814B7697F6
❑ 可通过如下链接查看：
https://goto.etherscan.com/address/0x11b815efb8f581194ae79006d24e0d814b7697f6
2. 获取交易数据的API参考文档
https://dune.com/home
https://thegraph.com/docs/zh/
https://github.com/binance/binance-spot-api-docs
https://docs.etherscan.io/
## 参考文献：
1. Heimbach L, Pahari V, Schertenleib E. Non-atomic arbitrage in decentralized
finance[C]//2024 IEEE Symposium on Security and Privacy (SP). IEEE, 2024: 3866-3884.
2. Wu F, Sui D, Thiery T, et al. Measuring CEX-DEX Extracted Value and Searcher Profitability:
The Darkest of the MEV Dark Forest[J]. arXiv preprint arXiv:2507.13023, 2025.