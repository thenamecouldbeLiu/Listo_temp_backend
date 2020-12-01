import pandas as pd
import numpy as np
import requests
import re
import os
from matplotlib import pyplot as plt

"""#抓取市場資訊
url = 'https://data.coa.gov.tw/Service/OpenData/FromM/FarmTransData.aspx?Crop=%E6%A4%B0%E5%AD%90&StartDate=109.09.22&EndDate=109.11.22'
download = requests.get(url)
download.encoding ="UTF-8"
data = download.json()"""
#data_DF = pd.DataFrame(data)
#data_DF.to_csv("cur_dir+coconut_market.csv", encoding="UTF-8-sig")

#資料前處理
cur_dir = os.getcwd()+"/"
data = pd.read_csv("C:\\Users\\YUZHI\\Desktop\\Jupyter\\coconut_market.csv")
print(data.head())


