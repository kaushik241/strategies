#!/usr/bin/env python
# coding: utf-8

# In[10]:


apikey = 'RdkCb8Gf'
username = 'K522839'
pwd = 'Kartik#5472'


# In[11]:


def conv(row):
    if(row['exits']==1):
        x=-1
        return x
    else:
        return 0


# In[12]:


from smartapi import SmartConnect
import time as tt
import requests
import websocket, json
import pandas as pd
from datetime import datetime,date,time 
from dateutil.relativedelta import relativedelta
import pandas_ta as ta
import vectorbt as vbt
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import mplfinance as mpf


st.set_page_config(page_title='Zelma Option Dashboard', page_icon=':tada:')
st.title('Zelma Option Dashboard')
st.header('Nifty 30 min Chart')

obj=SmartConnect(api_key=apikey)
data = obj.generateSession(username,pwd)
#print(data)
refreshToken= data['data']['refreshToken']
res = obj.getProfile(refreshToken)
#res['data']['exchanges'] 


# In[5]:



def getCandleData(symbolInfo):
    try:
        historicParam={
        "exchange": symbolInfo.exch_seg,
        "symboltoken": symbolInfo.token,
        "interval": "THIRTY_MINUTE",
        "fromdate": f'{(date.today()-relativedelta(days=30))} 09:15' , 
        "todate": f'{date.today()} 15:30' 
        }
        res_json=  obj.getCandleData(historicParam)
        columns = ['timestamp','open','high','low','close','volume']
        df = pd.DataFrame(res_json['data'], columns=columns)
        df['timestamp'] = pd.to_datetime(df['timestamp'],format = '%Y-%m-%dT%H:%M:%S')
        df['symbol'] = symbolInfo.symbol
        df['expiry'] = symbolInfo.expiry
        print(f"Done for {symbolInfo.symbol}")
        tt.sleep(0.2)
        return df
    except Exception as e:
        print(f"Historic Api failed: {e} {symbolInfo.symbol}")


# In[8]:


def check():
    x={'token': '53735',
       'symbol': 'NIFTY28JUL22FUT',
       'name': 'NIFTY', 
       'expiry': date(2022, 7, 28),
       'strike': -1.0,
       'lotsize': '50',
       'instrumenttype': 'FUTIDX',
       'exch_seg': 'NFO', 
       'tick_size': '5.000000'}   

    bnnifty_list=pd.DataFrame([x])

    eqdfList = []
    print(datetime.now())
    for i in bnnifty_list.index :
        try:
            symbol = bnnifty_list.loc[i]
            candelRes = getCandleData(symbol)
            eqdfList.append(candelRes)
        except Exception as e:

            print(f"Fetching Hist Data  failed {symbol.symbol} : {e}")

    print(datetime.now())

    NFOBNNIFTYFinalDf = pd.concat(eqdfList, ignore_index = True)
    nifty=NFOBNNIFTYFinalDf
    nifty['timestamp']=pd.to_datetime(nifty['timestamp'].apply(str).apply(lambda x:x.split('+')[0]), format='%Y-%m-%d %H:%M:%S' )

    nifty.set_index('timestamp',inplace=True)

    zlma = vbt.pandas_ta('zlma').run(nifty['close'],50)

    nifty['entries'] = zlma.zl_ema_crossed_above(zlma.zl_ema.shift(1)) 
    nifty['exits'] = zlma.zl_ema_crossed_below(zlma.zl_ema.shift(1))
    entries = zlma.zl_ema_crossed_above(zlma.zl_ema.shift(1)) 
    exits = zlma.zl_ema_crossed_below(zlma.zl_ema.shift(1))
    pf = vbt.Portfolio.from_signals(nifty['close'], entries = entries, exits = exits,short_entries=exits,short_exits=entries)   
    
    nifty['entries']=nifty['entries'].apply(int)
    nifty['exits']=nifty['exits'].apply(int)
    nifty['atm'] = 50*round(nifty['close']/50)
    nifty['exits']= nifty.apply(conv, axis=1)
    nifty['zlma']=ta.zlma(close=nifty['close'],length=45)

    nifty['Buy']=np.nan        
    nifty['Sell']=np.nan

    nifty.reset_index(inplace=True)
    for index,row in nifty.iterrows():
        if(row['entries']==1):
            nifty['Buy'].iloc[index]= row['close']-100
        if(row['exits']==-1):
            nifty['Sell'].iloc[index]= row['close']+100

    nifty.set_index('timestamp',inplace=True)
    
    st.set_option('deprecation.showPyplotGlobalUse', False)

    pos = nifty[(nifty['entries']==1) | (nifty['exits']==-1)]
    pos.reset_index(inplace=True)
    pos = pos[-4:]
    pos.set_index('timestamp',inplace=True)
    nifty  = nifty['2022-07-01':]
    apd = [mpf.make_addplot(nifty['zlma'],type='line'),mpf.make_addplot( nifty['Buy'], type = 'scatter', markersize= 200,marker='^', color='g'),mpf.make_addplot( nifty['Sell'], type = 'scatter', markersize= 200,marker='v',color='r')]  
    fig=mpf.plot(nifty,type='candle', figratio=(20,13), volume=True,addplot=apd,figsize=(15,10))
    st.pyplot(fig)
    pos.drop(['open','high','low','expiry','zlma','Buy','Sell'], axis=1,inplace=True)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.header('Last few trades')
    stats = pf.trades.records_readable
    st.dataframe(stats[-4:])
    #st.dataframe(pos)
    


# In[9]:


st.button('Get current position', on_click=check())


# In[ ]:




