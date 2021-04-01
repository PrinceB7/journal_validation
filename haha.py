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
aff = pd.read_csv('count_page.csv')
s = pd.read_csv('authors_val_h.csv')