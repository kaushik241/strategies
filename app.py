#!/usr/bin/env python
# coding: utf-8

# In[6]:
import pytz


import yfinance as yf
import datetime as dt
import datetime as datetime
import time
from nsepy import get_history
import numpy as np
import pandas as pd
import pandas_ta as ta
import requests
from bs4 import BeautifulSoup
import streamlit as st
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title='Anomalies Dashboard', page_icon=':tada:',layout='wide')
st.title('Strategies Dashboard')


def datetotimestamp(date):
    time_tuple = date.timetuple()
    timestamp= round(time.mktime(time_tuple))
    return timestamp

def timestamptodate(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

# In[7]:


df=pd.DataFrame()
df = yf.download('^NSEI',interval = '1d', period='1y')

master=pd.read_csv('Trading Patterns Anomalies 2022_Updated.csv')

df.reset_index(inplace=True)


# In[8]:


#1 Percentage Change
df['%Change'] = df['Adj Close']/df['Close'].shift(1)-1
#2 20 day Low
df['20_DL'] = np.where((df.Close<=df.Close.rolling(20).min()),'20 DL'," ")
#3 Weekday
df['week'] = df['Date'].apply(lambda x: x.weekday())
#4 RSI 2
df['RSI2'] = ta.rsi(df['Adj Close'], timeperiod = 2)
#5 3 Day High
df['3DH'] = df['3DH'] = np.where((df.Close >= df.Close.rolling(3).max()),'3DH'," ")
#6 Outside Day
df['Outside_Day'] = np.where(((df['High'] > df['High'].shift(1)) & (df['Low'] < df['Low'].shift(1))),"Outside Day"," ")
#7 RSI 3 on Abs. Change
df['RSI3_Abs_Change'] = ta.rsi((df['Adj Close'] - df['Adj Close'].shift(1)), timeperiod = 3)
#8 200 EMA
df['200_EMA'] = ta.ema(df['Adj Close'], timeperiod = 200)
#9 200 SMA
df['200_SMA'] = ta.sma(df['Adj Close'], timeperiod = 200)
#10 Pivot Points
df['PP'] = (df['High'].shift(1) + df['Low'].shift(1) + df['Close'].shift(1))/3
#11 S1
df['S1'] = (2*df['PP'] - (df['High'].shift(1)))
#12 R1
df['R1'] = (2*df['PP'] - (df['Low'].shift(1)))
#13 R2
df['R2'] = df['PP'] + (df['High'].shift(1) - df['Low'].shift(1))
#14 RSI10
df['RSI10'] = ta.rsi(df['Adj Close'], timeperiod = 10)


# In[9]:


start=datetotimestamp(datetime.datetime.now().date()-relativedelta(days=40)+datetime.timedelta(hours=9.5))
end= datetotimestamp(datetime.datetime.now().date()+datetime.timedelta(hours=9.4))
url='https://priceapi.moneycontrol.com/techCharts/history?symbol=36&resolution=1D&from='+str(start) + '&to=' +str(end)

resp=requests.get(url).json()
data=pd.DataFrame(resp)

date = []
for dt in data['t']:
    date.append({'Date':timestamptodate(dt).date()})
dt= pd.DataFrame(date)

vixnew = pd.concat([dt,data['c']],axis=1)

vixnew.columns = ['Date', 'Close']
vixnew['10_SMA'] = ta.sma(vixnew['Close'], timeperiod = 10)
vixnew['RSI2'] = ta.rsi(vixnew['Close'], timeperiod = 2)

start
end

st.dataframe(df)
st.dataframe(vixnew)





