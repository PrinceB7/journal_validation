#install textract, nltk, bs4, fuzzywuzzy
import textract
import difflib
import pandas as pd
import numpy as np
import requests
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from bs4 import BeautifulSoup as bs
import time
import random
from fuzzywuzzy import fuzz 	

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re



data = pd.read_csv('title_page.csv')
#number, title, form, date, publisher
x = data[['사번', '연번', '저서명(원어)', '저서형태', '출판년월', '출판사']]
c = pd.read_csv('count_page.csv')
s = pd.read_csv('authors_val_h.csv')


ix = 8
s_count = s.iloc[ix]['Author_Number']
print('s_count: ', s_count)	
x_id = x.iloc[ix]['사번']
x_num = x.iloc[ix]['연번']

sss = c[(c["사번"]==x_id) & (c["논문연번"]==x_num)]
print('\nsss: ' , sss)
print('\nlength: ' , len(sss))

