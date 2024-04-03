# 导入包
import pandas as pd
import akshare as ak
import streamlit as st
import riskfolio as rp
from common_functions import *
# 在matplotlib绘图中显示中文和负号
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
warnings.filterwarnings('ignore')
plt.rcParams["font.sans-serif"]=["SimHei"] # 设置字体
plt.rcParams['axes.unicode_minus'] = False   # 解决坐标轴负数的负号显示问题
import seaborn as sns
import matplotlib.pyplot as plt

# streamlit 框架


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
                     '001668', # 汇添富全球互联混合（和纳100相关性太高）
                     '006282',
                     '000043', # 嘉实美国成长（和纳100相关性太高）
                     '164701',
                     '164824', # 印度（目前暂停买入）
                     '519191',
                     '000893', # 工银创新动力
                     '001593',
                     ]
price_df = read_and_merge_fund_price(index_list)

st.title('基金相关性分析')

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
    for j in range(i+1, len(correlation_matrix.columns)):
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