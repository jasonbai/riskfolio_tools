import pandas as pd
import numpy as np
import akshare as ak
import os

# 获取基金基本信息函数并储存到本地
def get_fund_basic_info(sw_index_list, filename):
    # 确保data目录存在
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 构建完整的文件路径
    file_path = os.path.join(data_dir, filename)

    fund_df = pd.DataFrame()
    i = 0
    for code in sw_index_list:
        bars = ak.fund_individual_basic_info_xq(symbol=code)
        bars.index = bars['item']
        fund_df[code] = bars['value']
        i += 1
        print(f"\r已获取[{i}/{len(sw_index_list)}]支基金的数据", end="")
    fund_df.columns = sw_index_list

    # 将数据存储到CSV文件
    fund_df.to_csv(file_path)
    print(f"\n数据已存储到 {file_path}")


# 筛选符合年限的基金
def filter_funds_by_years(filename, year):
    # 构建完整的文件路径
    file_path = os.path.join('data', filename)

    # 从CSV文件中读取数据
    fund_df = pd.read_csv(file_path, index_col=0)

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
    return index_list

# 获取基金净值数据并存储到本地
def save_fund_price_to_local(index_list):
    for code in index_list:
        bars = ak.fund_open_fund_info_em(symbol=code, indicator="累计净值走势")
        bars['净值日期'] = pd.to_datetime(bars['净值日期']).dt.strftime('%Y-%m-%d')
        bars.index = pd.to_datetime(bars['净值日期'])
        bars.to_csv(os.path.join('data', f'{code}.csv'))
        print(f"已保存基金{code}的净值数据到本地")

# 从本地读取数据并合并
def read_and_merge_fund_price(index_list):
    price_df = pd.DataFrame()

    for code in index_list:
        file_path = os.path.join('data', f'{code}.csv')
        if os.path.exists(file_path):
            # 使用 parse_dates 参数将索引列解析为日期类型
            bars = pd.read_csv(file_path, index_col=0, parse_dates=[0])
            price_df[code] = bars['累计净值']

        else:
            print(f"找不到基金{code}的本地数据")

    price_df.columns = index_list
    return price_df