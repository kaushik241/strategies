#!/usr/bin/env python
# coding: utf-8

# In[6]:


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

st.set_page_config(page_title='Anomalies Dashboard', page_icon=':tada:',layout='wide')
st.title('Strategies Dashboard')
from dateutil.relativedelta import relativedelta


# In[7]:


df=pd.DataFrame()
df = yf.download('^NSEI',interval = '1d', period='1y')

def send_tel_alert(textsend):
    bot = telepot.Bot('5462022348:AAGk-ZvpMZhlr544CuMMTOOXY4CG14mfsEU')
    #bot.sendPhoto('821786933', photo=open('test1.png', 'rb'))
    bot.sendMessage('821786933', text=textsend)
#@myalertbot1234

master=pd.read_csv('/Users/test/Documents/Trading/Tele Alerts AB FINAL HAIN 30 Strategy copy heroku/Trading Patterns Anomalies 2022_Updated.csv')

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
df['200_SMA'] = ta.ma(df['Adj Close'], timeperiod = 200)
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


today = datetime.datetime.now().date()-relativedelta(days=1)

past = datetime.datetime.now().date()- relativedelta(days=25)

vix = get_history(symbol="INDIAVIX",
            start=past,
            end=today,
            index=True)

stock_url='https://www.moneycontrol.com/indian-indices/india-vix-36.html'

response = requests.get(stock_url)
print(response)

soup = BeautifulSoup(response.text, 'html.parser')
data_array = soup.find(id='mc_mainWrapper').getText().strip('').split('\n')

data_array = list(filter(None, data_array))
cur_vix=float(data_array[2])

vixnew=pd.DataFrame(vix["Close"])

vixnew.append({'Close':cur_vix},ignore_index=True)
vixnew['10_SMA'] = ta.MA(vixnew['Close'], timeperiod = 10)
vixnew['RSI2'] = ta.RSI(vixnew['Close'], timeperiod = 2)

conditions_met=pd.DataFrame(columns=['conditions_met'])
#conditions_met = conditions_met.append({'conditions_met':3},ignore_index=True)


# In[10]:


def check():
    conditions_met=pd.DataFrame(columns=['conditions_met'])
    #1. Fri-Mon Effect. Fri <= 0
    if((df['%Change'].iloc[-1] <= 0) & (df['week'].iloc[-1] == 4)):
        conditions_met = conditions_met.append({'conditions_met':1},ignore_index=True)

    #2. Fri-Mon Effect. Fri > 0
    if((df['%Change'].iloc[-1] > 0) & (df['week'].iloc[-1] == 4)):
        conditions_met = conditions_met.append({'conditions_met':2},ignore_index=True)

    #3. Fri-Mon Effect. Fri > 1%
    if((df['%Change'].iloc[-1] > 0.01) & (df['week'].iloc[-1] == 4)):
        conditions_met = conditions_met.append({'conditions_met':3},ignore_index=True)

    #4. Counter Trend Tues
    if((df['%Change'].iloc[-1] <= -0.01) & (df['week'].iloc[-1] == 0)):
        conditions_met = conditions_met.append({'conditions_met':4},ignore_index=True)

    #5. Thurs < -1%
    if((df['%Change'].iloc[-1] <= -0.01) & (df['week'].iloc[-1] == 3)):
        conditions_met = conditions_met.append({'conditions_met':5},ignore_index=True)

    #6. 20 Day Low (Fri)
    if((df['20_DL'].iloc[-1] == '20 DL') & (df['week'].iloc[-1] == 4)):
        conditions_met = conditions_met.append({'conditions_met':6},ignore_index=True)

    #7. 20 Day Low (Mon)
    if((df['20_DL'].iloc[-1] == '20 DL') & (df['week'].iloc[-1] == 0)):
        conditions_met = conditions_met.append({'conditions_met':7},ignore_index=True)

    #8. 20 Day Low (Wed) & Thurs > 0
    if((df['20_DL'].iloc[-2] == '20 DL') & (df['week'].iloc[-1] == 3) & (df['%Change'].iloc[-1] > 0)):
        conditions_met = conditions_met.append({'conditions_met':8},ignore_index=True)

    #9. RSI(3) on Daily Abs. Change (Mon) < 30
    if((df['RSI3_Abs_Change'].iloc[-1] < 30) & (df['week'].iloc[-1] == 0)):
        conditions_met = conditions_met.append({'conditions_met':9},ignore_index=True)

    #10. RSI(3) on Daily Abs. Change (Fri)
    if((df['RSI3_Abs_Change'].iloc[-1] < 30) & (df['week'].iloc[-1] == 4)):
        conditions_met = conditions_met.append({'conditions_met':10},ignore_index=True)

    #11. RSI(3) on Daily Abs. Change (Mon) > 70
    if((df['RSI3_Abs_Change'].iloc[-1] > 70) & (df['week'].iloc[-1] == 0)):
        conditions_met = conditions_met.append({'conditions_met':11},ignore_index=True)

    #12. Outside Day Pattern BTST on Wed < 0
    if((df['Outside_Day'].iloc[-1] == 'Outside Day') & (df['week'].iloc[-1] == 2) & (df['%Change'].iloc[-1] <= 0)):
        conditions_met = conditions_met.append({'conditions_met':12},ignore_index=True)

    #13. 2 Period RSI and Close < 200 EMA on Mon
    if((df['Adj Close'].iloc[-1] < df['200_EMA'].iloc[-1]) & (df['week'].iloc[-1] == 0) & (df['RSI2'].iloc[-1] <= 5)):
        conditions_met = conditions_met.append({'conditions_met':13},ignore_index=True)

    #14. 2 Period RSI and Close > 200 EMA on Thurs
    if((df['Adj Close'].iloc[-1] > df['200_EMA'].iloc[-1]) & (df['week'].iloc[-1] == 3) & (df['RSI2'].iloc[-1] <= 5)):
        conditions_met = conditions_met.append({'conditions_met':14},ignore_index=True)

    #15. 3 Days High & RSI2 > 90 on Fri
    if((df['3DH'].iloc[-1] == '3DH') & (df['week'].iloc[-1] == 4) & (df['RSI2'].iloc[-1] > 90)):
        conditions_met = conditions_met.append({'conditions_met':15},ignore_index=True)

    #16. Cum. RSI(2) (3 Days) < 35 & Close > 200 SMA
    if( ((df['RSI2'].iloc[-1]+df['RSI2'].iloc[-2]+df['RSI2'].iloc[-3])<35) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):   
        conditions_met = conditions_met.append({'conditions_met':16},ignore_index=True)

    #17. Cum. RSI(2) (2 Days) < 35 & Close > 200 SMA
    if( ((df['RSI2'].iloc[-1]+df['RSI2'].iloc[-2])<35) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):
        conditions_met = conditions_met.append({'conditions_met':17},ignore_index=True)

    #18 Cum. RSI(2) (2 Days) < 50 & Close > 200 SMA
    if( ((df['RSI2'].iloc[-1]+df['RSI2'].iloc[-2])<50) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):
        conditions_met = conditions_met.append({'conditions_met':18},ignore_index=True)

    #19 Close = 7 Day Low & Close > 200 SMA
    if( ((np.amin(df['Adj Close'][-7:]))==df['Adj Close'].iloc[-1]) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ): 
        conditions_met = conditions_met.append({'conditions_met':19},ignore_index=True)

    #20 Close is up 4 days in a row & Close < 200 SMA
    if( (df['%Change'].iloc[-4] > 0) & (df['%Change'].iloc[-3] > 0) & (df['%Change'].iloc[-2] > 0) & (df['%Change'].iloc[-1] > 0) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1])):
        conditions_met = conditions_met.append({'conditions_met':20},ignore_index=True)

    #21 RSI(2) of VIX > 90 & VIX Close > Previous Day VIX & RSI(2) Index < 30 & Close > 200 EMA
    if( (vixnew['RSI2'].iloc[-1]>90) & (vixnew['Close'].iloc[-1] > vixnew['Close'].iloc[-2]) &  (df['RSI2'].iloc[-1]<30)  &   (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):
        conditions_met = conditions_met.append({'conditions_met':21},ignore_index=True)

    #22 VIX > 5% of 10 DMA (VIX) at least 3 Days & Close > 200 SMA
    if( (vixnew['Close'].iloc[-1] > (1.05*vixnew['10_SMA'].iloc[-1])) & (vixnew['Close'].iloc[-1] > (1.05*vixnew['10_SMA'].iloc[-2])) & ((vixnew['Close'].iloc[-1]) > (1.05*vixnew['10_SMA'].iloc[-3]))  &   (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):         
        conditions_met = conditions_met.append({'conditions_met':22},ignore_index=True)

    #23 RSI(2) < 5 & Close > 200 SMA
    if( (df['RSI2'].iloc[-1] < 5) & (df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) ):
        conditions_met = conditions_met.append({'conditions_met':23},ignore_index=True)

    #24 Friday Pivot Points v1
    if( (df['week'].iloc[-1] == 4) & (df['%Change'].iloc[-2] < 0 ) & (df['%Change'].iloc[-1] < 0 ) & (df['Open'].iloc[-1] > df['Adj Close'].iloc[-2]) & (df['High'].iloc[-1] > df['R1'].iloc[-1])):
        conditions_met = conditions_met.append({'conditions_met':24},ignore_index=True)

    #25 Friday Pivot Points v2
    if((df['Open'].iloc[-1] > df['S1'].iloc[-1]) & (df['Open'].iloc[-1] < df['R1'].iloc[-1]) & (df['High'].iloc[-1] > df['R2'].iloc[-1]) & (df['Low'].iloc[-1] > df['S1'].iloc[-1]) & (df['Adj Close'].iloc[-1] > df['R1'].iloc[-1])):                 
        conditions_met = conditions_met.append({'conditions_met':25},ignore_index=True)

    #26 Monday 20 Day Low Pivot Points
    if((df['week'].iloc[-1] == 0) & (df['High'].iloc[-1] < df['R1'].iloc[-1]) & (df['20_DL'].iloc[-1] == '20 DL') & (df['Adj Close'].iloc[-1] < df['R1'].iloc[-1])):
        conditions_met = conditions_met.append({'conditions_met':26},ignore_index=True)

    #27 Monday Pivot Points v2
    if((df['week'].iloc[-1] == 0) & (df['%Change'].iloc[-1] < 0) & (df['%Change'].iloc[-2] < 0) & (df['Open'].iloc[-1] > df['Adj Close'].iloc[-2]) & (df['High'].iloc[-1] < df['R1'].iloc[-1])):
        conditions_met = conditions_met.append({'conditions_met':27},ignore_index=True)

    #28 Wednesday Pivot Points
    if((df['week'].iloc[-1] == 2) & (df['Open'].iloc[-1] > df['Adj Close'].iloc[-2]) & (df['%Change'].iloc[-1] > 0) & (df['Adj Close'].iloc[-1] > df['R1'].iloc[-1]) & (df['Low'].iloc[-1] > df['S1'].iloc[-1]) & (df['%Change'].iloc[-3] < 0)):    
        conditions_met = conditions_met.append({'conditions_met':28},ignore_index=True)

    #29 Monday Dip Pivot Points
    if((df['week'].iloc[-1] == 0) & (df['Open'].iloc[-1] < df['Adj Close'].iloc[-2]) & (df['%Change'].iloc[-2] < 0) & (df['High'].iloc[-1] < df['R1'].iloc[-1]) & (df['Low'].iloc[-1] < df['S1'].iloc[-1]) & (df['Adj Close'].iloc[-1] > df['S1'].iloc[-1]) & (df['Adj Close'].iloc[-1] < df['R1'].iloc[-1])):    
        conditions_met = conditions_met.append({'conditions_met':29},ignore_index=True)

    #30 RSI(10)<30 & Close > 200 SMA
    if((df['Adj Close'].iloc[-1] > df['200_SMA'].iloc[-1]) & (df['RSI10'].iloc[-1] <= 30)):
        conditions_met = conditions_met.append({'conditions_met':30},ignore_index=True)

    
    conditions_met=conditions_met.sort_values('conditions_met')

    display=pd.DataFrame(columns = master.columns)

    for index,row in conditions_met.iterrows():
        display = display.append(master[master['Condition']==row['conditions_met']])
    
 
    if(len(display)==0):
        st.header('No Conditions met today')
    if(len(display)!=0):
        st.dataframe(display)





# In[11]:


def send_alert():

    try:
        if(len(conditions_met)==0):
            x=datetime.datetime.today().date()
            print(x)
            send_tel_alert('No alert for {}'.format(x))

        else:
             for index,row in conditions_met.iterrows():
                x=row['conditions_met']
                for index,row in master.iterrows():
                    if(row['Condition']==x):
                        textsend = 'Condition: ' + str(row['Condition']) + os.linesep+ 'Instrument: ' + str(row['Instrument']) + os.linesep+ 'Type: ' + str(row['Type']) + os.linesep+ 'Long/Short: ' + str(row['Long/Short']) + os.linesep+ 'Entry: ' + str(row['Entry']) + os.linesep+ 'Exit: ' + str(row['Exit']) + os.linesep+ 'Profit Factor: ' + str(row['Profit Factor']) + os.linesep+ 'Win Days: ' + str(row['Win Days']) 
                        send_tel_alert(textsend)

    except:
        if(len(conditions_met)==0):
            send_tel_alert('No alert for today')

        else:
             for index,row in conditions_met.iterrows():
                x=row['conditions_met']
                for index,row in master.iterrows():
                    if(row['Condition']==x):
                        textsend = 'Condition: ' + str(row['Condition']) + os.linesep+ 'Instrument: ' + str(row['Instrument']) + os.linesep+ 'Type: ' + str(row['Type']) + os.linesep+ 'Long/Short: ' + str(row['Long/Short']) + os.linesep+ 'Entry: ' + str(row['Entry']) + os.linesep+ 'Exit: ' + str(row['Exit']) + os.linesep+ 'Profit Factor: ' + str(row['Profit Factor']) + os.linesep+ 'Win Days: ' + str(row['Win Days']) 
                        send_tel_alert(textsend)


# In[13]:


st.button('Get current conditions', on_click=check())

# In[ ]:





# In[ ]:




