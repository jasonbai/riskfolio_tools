# 导入包
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

import riskfolio as rp

from common_functions import *

# 在matplotlib绘图中显示中文和负号
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

plt.rcParams["font.sans-serif"]=["SimHei"] # 设置字体
plt.rcParams['axes.unicode_minus'] = False   # 解决坐标轴负数的负号显示问题

import warnings
warnings.filterwarnings('ignore')

# 设置页面标题和图标
st.set_page_config(page_title='资产组合分析工具', page_icon=":bar_chart:", layout='wide')
# 定义边栏导航
with st.sidebar:
    choose = option_menu('资产组合分析工具', ['组合评价', '相关性分析'],
                         icons=['house', 'bar_chart'])
if choose == '组合评价':
    st.title('资产组合投资分析-基金版本')
    index_list = ['040046',
                  '007380',
                  '015016',
                  '013308',
                  '162411',
                  '160416',
                  '000369',
                  '005613',
                  '007721',
                  '008763',
                  '001668',  # 汇添富全球互联混合（和纳100相关性太高）
                  '006282',
                  '000043',  # 嘉实美国成长（和纳100相关性太高）
                  '164701',
                  '164824',  # 印度（目前暂停买入）
                  '519191',
                  '000893',  # 工银创新动力
                  '001593',
                  ]

    price_df = read_and_merge_fund_price(index_list)
    st.markdown("## 基金基本信息")
    fund_info = pd.read_csv('data/fund_data.csv')
    st.write(fund_info)
    st.markdown("## 基金全部历史价格信息")
    st.write(price_df)

    # # 选取指定当日往回24个月范围的数据
    st.markdown("## 选取当日往回24个月范围的数据进行分析")
    from datetime import datetime, timedelta

    current_date = datetime.now()
    # 计算24个月前的日期
    start_date = current_date - timedelta(days=24 * 365 / 12)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = current_date.strftime('%Y-%m-%d')
    price_df = price_df[(price_df.index >= start_date_str) & (price_df.index <= end_date_str)]
    st.write(price_df)
    #
    st.title("最优组合及权重")
    # 计算资产收益率Y：
    Y = price_df.pct_change().dropna()
    # Building the portfolio object
    port = rp.Portfolio(returns=Y)
    # Calculating optimal portfolio
    # Select method and estimate input parameters:
    method_mu = 'hist'  # Method to estimate expected returns based on historical data.
    method_cov = 'hist'  # Method to estimate covariance matrix based on historical data.
    port.assets_stats(method_mu=method_mu, method_cov=method_cov, d=0.94)
    # Estimate optimal portfolio:
    model = 'Classic'  # Could be Classic (historical), BL (Black Litterman) or FM (Factor Model)
    rm = 'MV'  # Risk measure used, this time will be variance
    obj = 'Sharpe'  # Objective function, could be MinRisk, MaxRet, Utility or Sharpe
    hist = True  # Use historical scenarios for risk measures that depend on scenarios
    rf = 0  # Risk free rate
    l = 0  # Risk aversion factor, only useful when obj is 'Utility'

    w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)
    w_new = w.copy()
    w_new['权重'] = round(w['weights'] * 100, 2)
    fund_info.set_index('item', inplace=True)
    w_name = fund_info.loc['基金名称'].pipe(pd.DataFrame)
    folio = pd.concat([w_new, w_name], axis=1)
    folio = folio[folio['权重'] > 0].sort_values('权重', ascending=False)

    st.write(folio)

    st.markdown("## 绘制有效前沿")
    # 计算有效前沿
    # 设置有效前沿的点数
    points = 100

    # 计算有效前沿
    frontier = port.efficient_frontier(model=model, rm=rm, points=points, rf=rf, hist=hist)
    # 设置标签和其他参数
    label = '最大夏普比率投资组合'  # 点的标题
    mu = port.mu  # 预期收益
    cov = port.cov  # 协方差矩阵
    returns = port.returns  # 资产收益率
    # 创建一个matplotlib图表
    fig, ax = plt.subplots()

    # 绘制有效前沿
    ax = rp.plot_frontier(w_frontier=frontier, mu=mu, cov=cov, returns=returns, rm=rm, rf=rf, alpha=0.05,
                          cmap='viridis', w=w,
                          label=label, marker='*', s=16, c='r', height=6, width=10, ax=None)
    # 在Streamlit中展示图表
    st.pyplot(fig)

    # 绘制资产报告
    st.title("资产报告")
    returns = port.returns
    # 计算投资组合的有效前沿，即在给定的风险模型下，所有可能的资产组合的集合
    st.write("计算投资组合的有效前沿，所有可能的资产组合的集合：")
    fig, ax = plt.subplots()
    # Estimate points in the efficient frontier mean - semi standard deviation
    ws = port.efficient_frontier(model='Classic', rm=rm, points=20, rf=0, hist=True)
    ax = rp.plot_series(returns=Y,
                        w=ws,
                        cmap='tab20',
                        height=6,
                        width=10,
                        ax=None)
    st.pyplot(fig)

    # 计算投资组合的夏普比率最高的组合
    st.write("最大夏普比率投资组合：")
    fig, ax = plt.subplots()
    ax = rp.plot_drawdown(returns=Y,
                          w=w,
                          alpha=0.05,
                          height=8,
                          width=10,
                          ax=None)
    st.pyplot(fig)
    # 组合持仓
    st.write("组合持仓：")
    fig, ax = plt.subplots()
    ax = rp.plot_pie(w=w,
                     title='Portfolio',
                     height=6,
                     width=10,
                     cmap="tab20",
                     ax=None)
    st.pyplot(fig)
    fig, ax = plt.subplots()
    ax = rp.plot_bar(w,
                     title='Portfolio',
                     kind="v",
                     others=0.05,
                     nrow=25,
                     height=6,
                     width=10,
                     ax=None)
    st.pyplot(fig)

    st.write("收益矩阵：")
    fig, ax = plt.subplots()
    ax = rp.plot_hist(returns=Y,
                      w=w,
                      alpha=0.05,
                      bins=50,
                      height=6,
                      width=10,
                      ax=None)
    st.pyplot(fig)
elif choose == "相关性分析":
    st.title("基金相关性分析")
    index_list = ['040046',
                  '007380',
                  '015016',
                  '013308',
                  '162411',
                  '160416',
                  '000369',
                  '005613',
                  '007721',
                  '008763',
                  '001668',  # 汇添富全球互联混合（和纳100相关性太高）
                  '006282',
                  '000043',  # 嘉实美国成长（和纳100相关性太高）
                  '164701',
                  '164824',  # 印度（目前暂停买入）
                  '519191',
                  '000893',  # 工银创新动力
                  '001593',
                  ]
    price_df = read_and_merge_fund_price(index_list)

    st.title('基金基本信息')
    fund_info = pd.read_csv('data/fund_data.csv')
    st.write(fund_info)
    st.title('基金价格信息')
    st.write(price_df)

    # 计算相关性矩阵
    st.title('基金相关性矩阵')
    correlation_matrix = price_df.corr()
    st.write(correlation_matrix)

    # 使用seaborn绘制相关性矩阵的热图
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm',
                xticklabels=correlation_matrix.columns.values,
                yticklabels=correlation_matrix.columns.values)

    plt.title('Stock Correlation Matrix')
    plt.show()
    st.pyplot(plt)

    # 分析相关性较大的基金
    st.title('相关性较大的基金')

    # 让用户选择相关性阈值
    # 让用户输入相关性阈值
    threshold = st.number_input("输入相关性阈值，默认0.8", min_value=0.0, max_value=1.0, value=0.8, step=0.01)
    # 找出相关性大于0.9的股票对
    high_correlation_pairs = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i + 1, len(correlation_matrix.columns)):
            if abs(correlation_matrix.iloc[i, j]) > threshold:
                high_correlation_pairs.append((correlation_matrix.columns[i], correlation_matrix.columns[j]))

    # 解决出图标签为基金名称
    fund_info.set_index('item', inplace=True)
    fund_name = fund_info.loc['基金名称'].pipe(pd.DataFrame)
    fund_name = fund_name.rename_axis("股票代码")
    fund_name.reset_index(inplace=True)
    # 创建一个字典来映射股票代码到基金名称
    stock_to_fund_name = fund_name.set_index('股票代码')['基金名称'].to_dict()
    # 为每个相关性高的股票对绘制折线图
    for stock1, stock2 in high_correlation_pairs:
        plt.figure(figsize=(10, 5))
        fund_name1 = stock_to_fund_name.get(stock1, stock1)
        fund_name2 = stock_to_fund_name.get(stock2, stock2)
        plt.plot(price_df[stock1], label=fund_name1)
        plt.plot(price_df[stock2], label=fund_name2)
        plt.title(f'{fund_name1} vs {fund_name2}')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend()
        plt.show()
        st.pyplot(plt)