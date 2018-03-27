import requests
import pprint
import pandas as pd
import aiohttp
import asyncio
from datetime import date, timedelta


link = '''https://api.sensortower.com:443/v1/ios/sales_report_estimates?\
app_ids=1261357853&date_granularity=daily&start_date=2018-03-20&end_date=2018-03-25\
&auth_token=xsdUM_nD_2acJLMAr11T'''

# 5aaadaa79f479f794f3ef414 堡垒之夜 没有安卓的版本
# 55c5025102ac64f9c0001f96 coc的混合id
#r = requests.get(link)
#dict_list = r.json()
#df = pd.DataFrame(dict_list)
#df.fillna(0, inplace=True)
#df['Downloads'] = df['au'] + df['iu']
#df['Revenue'] = df['ar'] + df['ir']
#df1 = df.groupby('cc', as_index=False)['Downloads', 'Revenue'].sum()
#df1['Revenue'] = df1['Revenue'] / 100
#df1.sort_values('Downloads', inplace=True, ascending=False)
#if len(df1) > 10:
#    df2 = df1.iloc[:10, :]
#
#import seaborn as sns
#import matplotlib.pyplot as plt
#
#sns.set(style="whitegrid")
##sns.axes_style({'xtick.major.size': 1,
##                'ytick.major.size': 1})
#sns.set_context("notebook", font_scale=1.6)
##f, ax = plt.subplots(figsize=(20, 15))
#f, (ax1, ax2) = plt.subplots(1,2,sharey=True,figsize=(18, 6))
#grid = sns.factorplot(x="Downloads", y="cc",data=df2, ax=ax1,
#               kind="bar")
#for p in ax1.patches:
#    ax1.text(p.get_width(), p.get_y() + p.get_height()/2., '%d' % int(p.get_width()),
#            fontsize=13, color='black', ha='right', va='center')
#ax1.set(ylabel='Country')
#grid1 = sns.factorplot(x="Revenue", y="cc",data=df2, ax=ax2,
#               kind="bar")
#for p in ax2.patches:
#    ax2.text(p.get_width(), p.get_y() + p.get_height()/2., '%d' % int(p.get_width()),
#            fontsize=13, color='black', ha='right', va='center')
#ax2.set(ylabel='')
#f.subplots_adjust(hspace=1, wspace=0.2)
##f.tight_layout()
#
#f.savefig('/Users/yeye/Desktop/p.png')

def get_unified_id_url(unified_id):
    start_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
    base_url = 'https://api.sensortower.com:443/v1/unified/sales_report_estimates?app_ids='
    u_id = str(unified_id)
    end = '&date_granularity=daily&start_date={start_date}&end_date={end_date}&auth_token={token}'.format(start_date=start_date, end_date=end_date, token='xsdUM_nD_2acJLMAr11T')
    url = base_url + u_id + end
    return url

url = get_unified_id_url('5aaadaa79f479f794f3ef414')

async def get_my_app_info(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            info_list = await resp.json()
            df = pd.DataFrame(info_list)
    return df

task = asyncio.ensure_future(get_my_app_info(url))

def clean_df(df):
    android = pd.DataFrame()
    ios = pd.DataFrame()
    df.fillna(0, inplace=True)
    if ('android_units' and 'android_revenue') in df.columns:
        df['android_revenue'] = df['android_revenue'] / 100
        android = df.groupby('country')['android_revenue', 'android_units'].sum()
    if 'iphone_revenue' in df.columns:
        df['ios_revenue'] = (df['ipad_revenue'] + df['iphone_revenue']) / 100
        df['ios_units'] = df['ipad_units'] + df['iphone_units']
        ios = df.groupby('country')['ios_revenue', 'ios_units'].sum()
    return android, ios