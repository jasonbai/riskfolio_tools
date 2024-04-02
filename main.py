# 导入包
import pandas as pd
import akshare as ak
import streamlit as st
import riskfolio as rp
# 在matplotlib绘图中显示中文和负号
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
warnings.filterwarnings('ignore')
plt.rcParams["font.sans-serif"]=["SimHei"] # 设置字体
plt.rcParams['axes.unicode_minus'] = False   # 解决坐标轴负数的负号显示问题



# 定义函数，获取基金数据并获取某一年之前的基金列表
@st.cache_data
def get_fund_info(sw_index_list,year, return_fund_df=False):

    fund_df = pd.DataFrame()
    # 逐个获取指数行情数据
    i = 0
    for code in sw_index_list:
        bars = ak.fund_individual_basic_info_xq(symbol=code)
        bars.index = bars['item']
        fund_df[code] = bars['value']
        i += 1
        print(f"\r已获取[{i}/{len(sw_index_list)}]支基金的数据", end="")  # 输出处理进度
    fund_df.columns = sw_index_list

    # 获取某一年之前的基金列表
    fund_df_filtered = fund_df.loc['成立时间']
    # 将Series转换为DataFrame
    df = fund_df_filtered.reset_index()
    df.columns = ['index', 'date']
    # 将日期字符串转换为datetime对象
    df['date'] = pd.to_datetime(df['date'])
    df_before_data = df[df['date'].dt.year < year]

    # 输出最后的列表
    index_list = df_before_data['index'].tolist()

    if return_fund_df:
        return fund_df, index_list
    else:
        return index_list


# 定义函数，获取基金价格数据
@st.cache_data
def get_fund_price(index_list):
    price_df = pd.DataFrame()
    # 逐个获取指数行情数据
    i = 0
    for code in index_list:
        bars = ak.fund_open_fund_info_em(symbol=code, indicator="累计净值走势")
        bars['净值日期'] = pd.to_datetime(bars['净值日期']).dt.strftime('%Y-%m-%d')
        bars.index = pd.to_datetime(bars['净值日期'])
        price_df[code] = bars['累计净值']
        i += 1
        print("\r已获取[{}/{}]支基金的数据".format(i, len(index_list)), end="")  # 输出处理进度
    price_df.columns = index_list

    return price_df


# 确认入池
sw_index_list = ['040046',
                     '007380',
                     '015016',
                     '013308',
                     '162411',
                     '160416',
                     '000369',
                     '005613',
                     '007721',
                     '008763',
                     #'001668', # 汇添富全球互联混合（和纳100相关性太高）
                     '006282',
                     #'000043', # 嘉实美国成长（和纳100相关性太高）
                     '164701',
                    # '164824', # 印度（目前暂停买入）
                     '519191',
                     '000893', # 工银创新动力
                     '001593',
                     ]

# 创建一个文本输入框，用户可以输入新的产品代码
new_code = st.text_input("Enter a new product code to add:")

# 创建一个按钮，用户可以点击添加新的产品代码
if st.button("Add Product Code"):
    if new_code:
        sw_index_list.append(new_code)
        st.success(f"Product code '{new_code}' added successfully.")
 # 创建一个文本输入框，用户可以输入要删除的产品代码
code_to_remove = st.text_input("Enter a product code to remove:")
# 创建一个按钮，用户可以点击删除现有的产品代码
if st.button("Remove Product Code"):
    if code_to_remove in sw_index_list:
        sw_index_list.remove(code_to_remove)
        st.success(f"Product code '{code_to_remove}' removed successfully.")
    else:
        st.error(f"Product code '{code_to_remove}' not found in the list.")

# 输出某一年之前的基金列表
st.title("入池基金基本信息")
year = 2024
fund_df, index_list = get_fund_info(sw_index_list,year, return_fund_df=True)
st.write(fund_df)

# 输出资产池的历史价格
st.title("资产池历史价格")

price_df = get_fund_price(index_list)
# 选取指定当日往回24个月范围的数据
from datetime import datetime, timedelta
current_date = datetime.now()
# 计算24个月前的日期
start_date = current_date - timedelta(days=24*365/12)
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = current_date.strftime('%Y-%m-%d')
price_df = price_df[(price_df.index >= start_date_str) & (price_df.index <= end_date_str)]
st.write(price_df)

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
w_new['权重'] = round(w['weights']*100,2)
w_name=fund_df.loc['基金名称'].pipe(pd.DataFrame)
folio = pd.concat([w_new,w_name],axis=1)
folio = folio[folio['权重'] > 0].sort_values('权重', ascending=False)

st.write(folio)


st.markdown("## 绘制有效前沿")
# 计算有效前沿
# 设置有效前沿的点数
points = 100

# 计算有效前沿
frontier = port.efficient_frontier(model=model, rm=rm, points=points, rf=rf, hist=hist)
# 设置标签和其他参数
label = '最大夏普比率投资组合' # 点的标题
mu = port.mu # 预期收益
cov = port.cov # 协方差矩阵
returns = port.returns # 资产收益率
# 创建一个matplotlib图表
fig, ax = plt.subplots()

# 绘制有效前沿
ax = rp.plot_frontier(w_frontier=frontier, mu=mu, cov=cov, returns=returns, rm=rm, rf=rf, alpha=0.05, cmap='viridis', w=w,
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