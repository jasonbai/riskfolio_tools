# riskfolio_tools
 资产组合分析工具

## 介绍

riskfolio_tools 用于分析资产组合的风险和收益，计算有效前沿，并提供基金的相关性分析。它提供了以下功能：

- 计算资产组合的风险和收益
- 计算资产组合的有效前沿
- 计算资产组合的最大回撤、最大亏损、年化收益率、Sharpe 指数
- 提供基金的相关性分析

## 核心环境
前端框架：streamlit

后端框架：Python

## 依赖库
- Python 3.8
- akshare
- streamlit
- cvxpy
- riskfolio-lib

## 使用说明
先运行fund_download.py文件，该文件用于下载基金数据，并保存到本地。

启动软件：
```
python main.py
```