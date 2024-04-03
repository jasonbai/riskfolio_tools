# 导入包
import pandas as pd
import akshare as ak
import streamlit as st
from common_functions import *

# 确定要分析的基金
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
                     '001668', # 汇添富全球互联混合（和纳100相关性太高）
                     '006282',
                     '000043', # 嘉实美国成长（和纳100相关性太高）
                     '164701',
                     '164824', # 印度（目前暂停买入）
                     '519191',
                     '000893', # 工银创新动力
                     '001593',
                     ]
get_fund_basic_info(sw_index_list, 'fund_data.csv')
year = 2024
index_list = filter_funds_by_years('fund_data.csv', year)

save_fund_price_to_local(index_list)

price_df = read_and_merge_fund_price(index_list)
