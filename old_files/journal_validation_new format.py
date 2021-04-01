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


#getting data from form
title1 = 'Sparse Beamforming and User-Centric Clustering for downlink Cloud Radio Access Network'
doi1 = '//doi.org/10.1109/ACCESS.2014.2362860'
journal1 = 'IEEE Access'
author1 = 'Dai Binbin'
filename1 = 'pdf/11.pdf'

title2 = 'Predicting Entrepreneurial Intention of Students: An Extreme Learning Machine With gaussian barebone Harris Hawks Optimizer'
doi2 = '//doi.org/10.1109/ACCESS.2020.2982796'
journal2 = 'IEEE Access'
author2 = 'MINGJING WANG'
filename2 = 'pdf/21.pdf'

title5 = 'skill based transfer learning with domain adaptation for continuous reinforcement learning domains'
doi5 = '//doi.org/10.1007/s10489-019-01527-z'
journal5 = 'Applied Intelligence'
author5 = 'Farzaneh Shoeleh'
filename5 = 'pdf/51.pdf'

title7 = 'On-Device Partial Learning Technique of Convolutional Neural network for New Classes'
doi7 = '//doi.org/10.1007/s11265-020-01520-7'
journal7 = 'Journal of signal Processing Systems'
author7 = 'Cheonghwan Hur'
filename7 = 'pdf/71.pdf'


def main():
	#getting data from a file
	data = pd.read_excel('Data-2020-2.xlsx')
	print(data.values.shape)
	#english_name, korean_name, title, author_count, pages, author_rank
	x = data[['영문명(추가)', '성명', '제목', '저자수', '게재면', '역할']]
	print(x.shape)
	
	scopus = pd.read_csv('temp/un_scopus.csv')
	s = scopus[['Title', 'cor_A', 'Author', 'vol_num']]

	#kci = pd.read_csv('temp/un_kci.csv')
	#k = scopus[['Title', 'cor_A', 'Author', 'vol_num']] 


	'''
	#1st phase: validating and writing into csv file using scopus data
	for ix in range(0, 632):
		print("Now doing row number: ", ix)

		if s.iloc[ix]['Title'] == '0':
			print('skipping')
			x.loc[ix, 'val_title'] = 'unknown--'
			x.loc[ix, 'val_pages'] = 'unknown--'
			x.loc[ix, 'val_rank'] = 'unknown--'
			continue

		korean = x.iloc[ix]['성명']
		english = x.iloc[ix]['영문명(추가)']

		pages = s.iloc[ix]['vol_num'].split()
		pages = pages[len(pages)-1]
		title = s.iloc[ix]['Title']
		t_ind = title.find('(Article)')
		title = title[0 : t_ind-1 : ]
		author = s.iloc[ix]['Author']
		author_list = author.split("', ")
		cor_a = s.iloc[ix]['cor_A']


		if difflib.SequenceMatcher(None, x.iloc[ix]['제목'].lower(), title.lower()).ratio()>0.90:
			x.loc[ix, 'val_title'] = 'valid'
			#x.to_csv('paper.csv', index=False)
		else:
			th = "{:.2f}".format(difflib.SequenceMatcher(None, x.iloc[ix]['제목'].lower(), title.lower()).ratio())
			x.loc[ix, 'val_title'] = 'invalid ('+str(th)+')'

		if compare_name(x.iloc[ix]['게재면'], pages):
			x.loc[ix, 'val_pages'] = 'valid'
		else:
			x.loc[ix, 'val_pages'] = 'invalid'	


		#first author
		if x.iloc[ix]['역할'] == '제1저자':
			if compare_name(korean, author_list[0]) or compare_name(english, author_list[0]):
				x.loc[ix, 'val_rank'] = 'valid'
			else:
				x.loc[ix, 'val_rank'] = 'invalid'

		#co-author	
		elif x.iloc[ix]['역할'] == '공동저자' or x.iloc[ix]['역할'] == '공동':
			if coauthor_list(korean, author_list) or coauthor_list(english, author_list):
				x.loc[ix, 'val_rank'] = 'valid'
			else:
				x.loc[ix, 'val_rank'] = 'invalid'


		#corresponding author
		elif x.iloc[ix]['역할'] == '교신저자' or x.iloc[ix]['역할'] == '책임':
			if compare_name(korean, cor_a) or compare_name(english, cor_a):
				x.loc[ix, 'val_rank'] = 'valid'
			else:
				x.loc[ix, 'val_rank'] = 'invalid'

		else:
			x.loc[ix, 'val_rank'] = 'unknown++'	

		x.to_csv('paper.csv', index=False)

	print('\n\nDone------------\n\n')	
	'''


	#2nd phase: increase hitrate using WoS data
	print('\nI am performing the 2nd phase----\n')
	data2 = pd.read_csv('paper.csv')
	x2 = data2[['영문명(추가)', '성명', '제목', '저자수', '게재면', '역할', 'val_title', 'val_pages', 'val_rank']]

	wos_data = pd.read_csv('temp/un_wos_v2.csv')
	wos = wos_data[['Title', 'cor_A', 'Author', 'vol_num']]

	for ix in range(0, 632):
		print("Now doing row number: ", ix)

		if x2.iloc[ix]['val_title'] == 'unknown--' and wos.iloc[ix]['Title'] != '0':
			print('\n--------------I found new data at ', ix)

			korean = x2.iloc[ix]['성명']
			english = x2.iloc[ix]['영문명(추가)']

			pages = wos.iloc[ix]['vol_num']
			title = wos.iloc[ix]['Title']
			author = wos.iloc[ix]['Author']
			author_list = author.split("', ")
			cor_a = wos.iloc[ix]['cor_A']
			if cor_a.find("', "):
				cor_a = cor_a.split("', ")
			else:
				cor_a = cor_a.split("]")


			if difflib.SequenceMatcher(None, x2.iloc[ix]['제목'].lower(), title.lower()).ratio()>0.90:
				x2.loc[ix, 'val_title'] = 'valid'
				#x.to_csv('paper.csv', index=False)
			else:
				th = "{:.2f}".format(difflib.SequenceMatcher(None, x2.iloc[ix]['제목'].lower(), title.lower()).ratio())
				x2.loc[ix, 'val_title'] = 'invalid ('+str(th)+')'

			if compare_name(x2.iloc[ix]['게재면'], pages):
				x2.loc[ix, 'val_pages'] = 'valid'
			else:
				x2.loc[ix, 'val_pages'] = 'invalid'	


			#first author
			if x2.iloc[ix]['역할'] == '제1저자':
				if compare_name(korean, author_list[0]) or compare_name(english, author_list[0]):
					x2.loc[ix, 'val_rank'] = 'valid'
				else:
					x2.loc[ix, 'val_rank'] = 'invalid'

			#co-author	
			elif x2.iloc[ix]['역할'] == '공동저자' or x2.iloc[ix]['역할'] == '공동':
				if coauthor_list(korean, author_list) or coauthor_list(english, author_list):
					x2.loc[ix, 'val_rank'] = 'valid'
				else:
					x2.loc[ix, 'val_rank'] = 'invalid'


			#corresponding author
			elif x2.iloc[ix]['역할'] == '교신저자' or x2.iloc[ix]['역할'] == '책임':
				for k in range(0, len(cor_a)):
					if compare_name(korean, cor_a[k]) or compare_name(english, cor_a[k]):
						x2.loc[ix, 'val_rank'] = 'valid'
						break
					else:
						x2.loc[ix, 'val_rank'] = 'invalid'

			else:
				x2.loc[ix, 'val_rank'] = 'unknown++'	

			x2.to_csv('paper.csv', index=False)



	#2nd phase: increase hitrate using WoS data
	print('\nI am performing the 2nd phase----\n')
	data2 = pd.read_csv('paper.csv')
	x2 = data2[['영문명(추가)', '성명', '제목', '저자수', '게재면', '역할', 'val_title', 'val_pages', 'val_rank']]

	wos_data = pd.read_csv('temp/un_wos_v2.csv')
	wos = wos_data[['Title', 'cor_A', 'Author', 'vol_num']]

	for ix in range(0, 632):
		print("Now doing row number: ", ix)

		if x2.iloc[ix]['val_title'] == 'unknown--' and wos.iloc[ix]['Title'] != '0':
			print('\n--------------I found new data at ', ix)

			korean = x2.iloc[ix]['성명']
			english = x2.iloc[ix]['영문명(추가)']

			pages = wos.iloc[ix]['vol_num']
			title = wos.iloc[ix]['Title']
			author = wos.iloc[ix]['Author']
			author_list = author.split("', ")
			cor_a = wos.iloc[ix]['cor_A']
			if cor_a.find("', "):
				cor_a = cor_a.split("', ")
			else:
				cor_a = cor_a.split("]")


			if difflib.SequenceMatcher(None, x2.iloc[ix]['제목'].lower(), title.lower()).ratio()>0.90:
				x2.loc[ix, 'val_title'] = 'valid'
				#x.to_csv('paper.csv', index=False)
			else:
				th = "{:.2f}".format(difflib.SequenceMatcher(None, x2.iloc[ix]['제목'].lower(), title.lower()).ratio())
				x2.loc[ix, 'val_title'] = 'invalid ('+str(th)+')'

			if compare_name(x2.iloc[ix]['게재면'], pages):
				x2.loc[ix, 'val_pages'] = 'valid'
			else:
				x2.loc[ix, 'val_pages'] = 'invalid'	


			#first author
			if x2.iloc[ix]['역할'] == '제1저자':
				if compare_name(korean, author_list[0]) or compare_name(english, author_list[0]):
					x2.loc[ix, 'val_rank'] = 'valid'
				else:
					x2.loc[ix, 'val_rank'] = 'invalid'

			#co-author	
			elif x2.iloc[ix]['역할'] == '공동저자' or x2.iloc[ix]['역할'] == '공동':
				if coauthor_list(korean, author_list) or coauthor_list(english, author_list):
					x2.loc[ix, 'val_rank'] = 'valid'
				else:
					x2.loc[ix, 'val_rank'] = 'invalid'


			#corresponding author
			elif x2.iloc[ix]['역할'] == '교신저자' or x2.iloc[ix]['역할'] == '책임':
				for k in range(0, len(cor_a)):
					if compare_name(korean, cor_a[k]) or compare_name(english, cor_a[k]):
						x2.loc[ix, 'val_rank'] = 'valid'
						break
					else:
						x2.loc[ix, 'val_rank'] = 'invalid'

			else:
				x2.loc[ix, 'val_rank'] = 'unknown++'	

			x2.to_csv('paper.csv', index=False)		







	'''

	#for loop for google scholar data extraction for each author_rank
	for ix in range(12, 14):
		sleep_time = random.randint(7,10)
		print('\n', ix, ' - ', x.iloc[ix]['제목'], '\n')

		
		korean = x.iloc[ix]['성명']
		english = x.iloc[ix]['영문명(추가)']

		#fist author
		if x.iloc[ix]['역할'] == '제1저자':
			print('\nFirst author\n')
			all_authors, vancouver_authors, title, pages = google_scholar_selenium(x.iloc[ix]['제목'])


			options = webdriver.ChromeOptions()
		    driver = webdriver.Chrome("/home/prince/chromedriver", options = options)
		    Scopus_sign_in("vmfksxp89@gmail.com", "hyojae12!")
			journal, inst, vol, paper_type, title, cor_a, authors, link, err_type = extract_Scopus_title(x.iloc[ix]['제목'])



			print(x.iloc[ix]['제목'])
			print(korean, ' ; ', english)
			print('\nExtracted title and authors:')
			print(title)
			print(all_authors)
			if difflib.SequenceMatcher(None, x.iloc[ix]['제목'].lower(), title.lower()).ratio()>0.90:
				x.loc[ix, 'val_title'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid title to the file\n')
			else:
				th = "{:.2f}".format(difflib.SequenceMatcher(None, x.iloc[ix]['제목'].lower(), title.lower()).ratio())
				x.loc[ix, 'val_title'] = 'invalid ('+str(th)+')'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid title to the file\n')

			if compare_name_string(korean, vancouver_authors) or compare_name_string(english, vancouver_authors):
				x.loc[ix, 'val_rank'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid author_name to the file\n')
			else:
				x.loc[ix, 'val_rank'] = 'invalid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid author_name to the file\n')

			if difflib.SequenceMatcher(None, x.iloc[ix]['게재면'], pages).ratio()==1:
				x.loc[ix, 'val_pages'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid pages to the file\n')
			else:
				x.loc[ix, 'val_pages'] = 'invalid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid pages to the file\n')	
			time.sleep(sleep_time)

		#co-author	
		elif x.iloc[ix]['역할'] == '공동저자' or x.iloc[ix]['역할'] == '공동':	
			print('\nCo - author\n')
			all_authors, vancouver_authors, title, pages = google_scholar_selenium(x.iloc[ix]['제목'])


			print(x.iloc[ix]['제목'])
			print(korean, ' ; ', english)
			print('\nExtracted title and authors:')
			print(title)
			print(all_authors)
			if difflib.SequenceMatcher(None, x.iloc[ix]['제목'].lower(), title.lower()).ratio()>0.90:
				x.loc[ix, 'val_title'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid title to the file\n')
			else:
				th = "{:.2f}".format(difflib.SequenceMatcher(None, x.iloc[ix]['제목'].lower(), title.lower()).ratio())
				x.loc[ix, 'val_title'] = 'invalid ('+str(th)+')'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid title to the file\n')

			if search_for_coauthor(korean, vancouver_authors) or search_for_coauthor(english, vancouver_authors):
				x.loc[ix, 'val_rank'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid author_name to the file\n')
			else:	
				x.loc[ix, 'val_rank'] = 'invalid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid author_name to the file\n')

			if difflib.SequenceMatcher(None, x.iloc[ix]['게재면'], pages).ratio()==1:
				x.loc[ix, 'val_pages'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid pages to the file\n')
			else:
				x.loc[ix, 'val_pages'] = 'invalid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid pages to the file\n')	
			time.sleep(sleep_time)

		#corresponding author		
		elif x.iloc[ix]['역할'] == '교신저자' or x.iloc[ix]['역할'] == '책임':
			print('\nCorresponding author\n')
			all_authors, vancouver_authors, title, pages = google_scholar_selenium(x.iloc[ix]['제목'])


			print(x.iloc[ix]['제목'])
			print(korean, ' ; ', english)
			print('\nExtracted title and authors:')
			print(title)
			print(all_authors)
			if difflib.SequenceMatcher(None, x.iloc[ix]['제목'].lower(), title.lower()).ratio()>0.90:
				x.loc[ix, 'val_title'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid title to the file\n')
			else:
				th = "{:.2f}".format(difflib.SequenceMatcher(None, x.iloc[ix]['제목'].lower(), title.lower()).ratio())
				x.loc[ix, 'val_title'] = 'invalid ('+str(th)+')'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid title to the file\n')

			x.loc[ix, 'val_rank'] = 'corr_unknown'
			x.to_csv('paper.csv', index=False)

			if difflib.SequenceMatcher(None, x.iloc[ix]['게재면'], pages).ratio()==1:
				x.loc[ix, 'val_pages'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid pages to the file\n')
			else:
				x.loc[ix, 'val_pages'] = 'invalid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid pages to the file\n')

			time.sleep(sleep_time)
		else:
			print('\n', x.iloc[ix]['역할'])
			time.sleep(sleep_time)					


	'''		




	'''
	print("\nDBpia--------------------\n")
	Link, Title, Authors, Publisher = DBpia_title(x.iloc[2]['title'])
	print(Link)
	print(Title)
	print(Authors)
	print(Publisher)

	print(x.iloc[2]['title'])
	print('Large-eddy simulations of wind-farm wake characteristics associated with a low-level jet')
		
	print("\nWoS--------------------\n")
	Link, Title, Authors, cor_A = extract_WOS_title(x.iloc[2]['title'])
	print(Link)
	print(Title)
	print(Authors)
	print(cor_A)
	'''





	'''
	#extracting text using textract:
	print('\n\n--------------------------------Extract PDF----------------------------------\n\n')
	text2 = textract.process(filename7, method='pdfminer')
	text2 = text2.decode('utf-8')
	text2 = text2.replace("\n", " ")
	#print(text2)

	keyword = collect_keywords(text2)
	#keyword.insert(0, 'IEEE')
	#keyword.insert(1, 'Access')
	keyword = [each_key.lower() for each_key in keyword]
	#print('\n Keyssss:\n', keyword)
	validate_journal_doi(doi7, keyword)
	validate_title_from_pdf(title7, text2)
	validate_journal_name(journal7, text2)
	
	if validate_author_name(author7, text2) or validate_author_name_keywords(author7, keyword):
		print('\nAuthor name is validated\t==> ', author7)
	else:
		print("\nAuthor name did NOT match")
		print("Check the author name: ", author7)
	'''



	'''
	#working with not_full data
	not_full, authors = extract_author_names(raw_html_data)
	print('\nall author names: ', authors)
	author_rank = authors.split(',')
	print('\nfirst author: ', author_rank[0])
	if not_full:
		corresponding_author = 'unknown'
	else:
		corresponding_author = 	author_rank[len(author_rank)-1]
	print('\ncorresponding author: ', corresponding_author)
	'''

	
	

#----------------------------------Functions----------------------------------------
#----------------------------------Functions----------------------------------------
#----------------------------------Functions----------------------------------------
#----------------------------------Functions----------------------------------------
#----------------------------------Functions----------------------------------------



def google_scholar(title):
	google_title = make_title(title)
	url = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q="+google_title+"&btnG="
	#url = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&as_ylo=2020&q=new+algorithm+for+CNN&btnG="
	header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
	respon = requests.get(url, headers=header)
	code = respon.status_code
	not_full = True
	if code == 200:
		if respon.text.count('did not match any articles'):
			print('\n\n\n-----------------The title you searched did not match with any article on the web\n\n')
			return 'not_found', False, 'not_found'
		index = respon.text.find('class="gs_ri"')
		if index == -1:
			print('\n\n\n----------------------------Google Scholar error----------------------------\n\n\n')
			raw_html_data = ""
		else:	
			index2 = respon.text.find('data-clk-atid=', index+15)
			raw_html_data = respon.text[index2+14 : len(respon.text) : ]
	else:
		raw_html_data = ""
		print('Error in status code: ', code)

	if raw_html_data == "":
		_extracted_title = 'empty'
		_all_authors = 'empty'
		print("\n\n I did not receive any html data\n")
	else:
		_extracted_title = extract_title(raw_html_data)
		not_full, _all_authors = extract_author_names(raw_html_data)

	return _extracted_title, not_full, _all_authors


def google_scholar_selenium(title):
	options = webdriver.ChromeOptions()
	driver = webdriver.Chrome("/home/prince/chromedriver", options = options)
	driver.get("https://scholar.google.com/scholar?hl=en")
	time.sleep(2)
	elem = driver.find_element_by_name("q")
	elem.clear()
	elem.send_keys(title)
	elem.submit()
	time.sleep(2)

	viewbox = driver.find_element_by_xpath('//*[@id="gs_res_ccl_mid"]/div/div[2]/div[3]/a[2]')
	viewbox.click()
	time.sleep(2)
	#MLA = driver.find_element_by_xpath('//*[@id="gs_citt"]/table/tbody/tr[1]/td/div').text
	#APA = driver.find_element_by_xpath('//*[@id="gs_citt"]/table/tbody/tr[2]/td/div').text
	CHICAGO = driver.find_element_by_xpath('//*[@id="gs_citt"]/table/tbody/tr[3]/td/div').text
	Vancouver = driver.find_element_by_xpath('//*[@id="gs_citt"]/table/tbody/tr[5]/td/div').text
	#print("\nMLA : \n" + MLA)
	#print("\nAPA : \n" + APA)
	print("\nCHICAGO : \n" + CHICAGO)
	webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
	driver.close()
	index = CHICAGO.find('"')
	all_authors = CHICAGO[0 : index-2 : ]
	index2 = CHICAGO.find('"', index+2)
	title = CHICAGO[index+1 : index2-1 : ]
	index = CHICAGO.find('):')
	if index:
		pages = CHICAGO[index+3 : len(CHICAGO)-1 : ]
	else:
		pages = 'unknown'
	period = Vancouver.find('.')
	vancouver_authors = Vancouver[0 : period : ]	
	return all_authors, vancouver_authors, title, pages


driver = None
#   selenium에 error 발생시 재시작 해주는 함수
def selenium_initialize():
    global driver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome("D:/chromedriver.exe", options = options)


#   Title 명을 넣어주면 그에 해당하는 나머지 정보를 반환해주는 함수. extract_KCI_data 에서 사용됨.
def extract_KCI_title(t):
    global driver
    err_type = -1
    driver.get("https://www.kci.go.kr/kciportal/po/search/poArtiSearList.kci")

    elem = driver.find_element_by_name("poSearchBean.keyword4")
    elem.clear()
    elem.send_keys(t)
    elem.submit()
    time.sleep(1)
    
    journal, inst, vol, paper_type, title, cor_a, authors, link = None, None, None, None, None, None, None, None
    
    time.sleep(2)
    if driver.find_element_by_xpath('//*[@id="sBody"]/h3/span/em/strong[2]').text == '0':
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type
    elif driver.find_element_by_xpath('//*[@id="sBody"]/h3/span/em/strong[2]').text == '1':
        p_link = driver.find_element_by_xpath('//*[@id="poArtiSearList"]/table/tbody/tr/td[2]/p/label/a')
        p_link.click()
    else:
        p_link = driver.find_element_by_xpath('//*[@id="poArtiSearList"]/table/tbody/tr[1]/td[2]/p/label/a')
        p_link.click()
        time.sleep(1)
        
    link = driver.current_url
    all_data = driver.find_element_by_xpath('//*[@id="printArea"]/div[1]/div[1]').text.split("\n")
    journal = all_data[0]
    for i, v in enumerate(all_data):
        if "vol" in v:
            vol = v
        elif "발행기관" in v:
            inst = v[5:]
    try:
        title = driver.find_element_by_xpath('//*[@id="printArea"]/div[1]/p').text
    except:
        err_type = 5
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type
        
    try:
        authors = driver.find_element_by_xpath('//*[@id="printArea"]/div[1]/div[2]').text
        authors = authors.split(' ,  ')
        cor_a = []
        author = []
        if len(authors) == 1:
            first_a = authors[0]
            cor_a = authors[0]
        else:
            for a in authors:
                if '제1' in a:
                    author.insert(0, a)
                if '교신' in a:
                    cor_a.append(a)
                if '참여' in a:
                    author.append(a)
        authors = author
    except:
        err_type = 7
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type
    

    return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type

#   DataFrame을 인자로 받고 그에 해당하는 Data 추출. 알 수 없는 error 발생시 selenium initialization이 적용되어있는 함수
def extract_KCI_data(df):
    global driver
    newdf = pd.DataFrame(np.zeros((len(df['제목']), 5)), columns=['Title', 'Link', 'Authors', 'cor_A', 'inst'])

    options = webdriver.ChromeOptions()
    # you have to downloacd chrome driver
    # options.add_argument('headless') --> headless mode
    driver = webdriver.Chrome("D:/chromedriver.exe", options = options)
    
    newdf['Title'] = 'NULL'
    newdf['Link'] = 'NULL'
    newdf['Author'] = 'NULL'
    newdf['cor_A'] = 'NULL'
    newdf['inst'] = 'NULL'
    newdf['vol_num'] = 'NULL'
    newdf['paper_type'] = 'NULL'
    newdf['Journal'] = 'NULL'
    cnt = 0
    i = -1
    while True:
        try:
            err_cnt = 0
            while i < len(df['제목']) - 1:
                i+= 1
                if i < cnt:
                    continue
                print(str(i) + " : " + df['제목'][i])    
                journal, inst, vol, paper_type, title, cor_a, authors, link, err_type = extract_KCI_title(df['제목'][i])

                if err_type != -1:
                    if err_cnt < 5:
                        i -= 1
                        err_cnt += 1
                        continue
                    else:
                        cnt += 1
                        err_cnt = 0
                        continue
                cnt += 1
                newdf['Journal'][i] = journal
                newdf['inst'][i] = inst
                newdf['vol_num'][i] = vol
                newdf['paper_type'][i] = paper_type
                newdf['Title'][i] = title
                newdf['cor_A'][i] = cor_a
                newdf['Author'][i] = authors
                newdf['Link'][i] = link
            break
        except:
            i-=1
            selenium_initialize()
    return newdf



#   Title 명을 넣어주면 그에 해당하는 나머지 정보를 반환해주는 함수. extract_Scopus_data 에서 사용됨.
def extract_Scopus_title(t):
    global driver
    err_type = -1
    driver.get("https://scopus.com")
    journal, inst, vol, paper_type, title, cor_a, authors, link = None, None, None, None, None, None, None, None
    time.sleep(1)
    elem = driver.find_element_by_xpath('//*[@id="searchterm1"]')
    elem.clear()
    elem.send_keys(re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', ' ', t))
    elem.submit()
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    search = soup.find('h1', {'class':'documentHeader'}).get_text().split("\n")[0][1:]
    print(search)

    if search == 'Document search results':
        print("검색결과 없음")
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type

    elif search == '1 document result':
        time.sleep(3)
        try:
            sort = driver.find_element_by_xpath('//*[@id="navLoad-button"]/span[2]')
            sort.click()
            relevance = driver.find_element_by_xpath('//*[@id="ui-id-5"]')
            relevance.click()
        except:
            err_type = 0
            return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type

        print("1개 결과")
        p_link = driver.find_element_by_xpath('//*[@id="resultDataRow0"]/td[1]/a')
        p_link.click()
    elif search == 'Error':
        print("알 수 없는 에러")
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type

    else:
        time.sleep(3)
        try:
            sort = driver.find_element_by_xpath('//*[@id="navLoad-button"]/span[2]')
            sort.click()
            relevance = driver.find_element_by_xpath('//*[@id="ui-id-5"]')
            relevance.click()
        except:
            err_type = 0
            return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type

        print("여러개 결과")
        time.sleep(3)
        p_link = driver.find_element_by_xpath('//*[@id="resultDataRow0"]/td[1]/a')
        p_link.click()


    try:
        time.sleep(1)
        paper_data = driver.find_element_by_xpath('//*[@id="referenceInfo"]/div').text.split('\n')
        for a in paper_data:
            if "Document Type" in a:
                paper_type = a[15:]
            elif "Publisher" in a:
                inst = a[11:]
    except:
        err_type = 2
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type


    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    try:
        journal = soup.find("span", {'id':'publicationTitle'}).get_text()
    except:
        err_type = 3
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type

    try:
        vol = driver.find_element_by_xpath('//*[@id="journalInfo"]').text
    except:
        err_type = 4
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type

    try:
        title = driver.find_element_by_xpath('//*[@id="profileleftinside"]/div[2]/h2').text
    except:
        err_type = 5
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type


    try:
        cor_a = driver.find_element_by_xpath('//*[@id="profileleftinside"]/p').text
        cor_a = cor_a.split(';')[0][2:]
    except:
        err_type = 6
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type


    try:
        authors = soup.find('section', {'id':'authorlist'})
        links = authors.find_all("a", {'title':'Show Author Details'})

        hrefs=[]
        for a in links:
            hrefs.append(a.attrs['href'])

        authors = []
        for a in hrefs:
            driver.get(a)
            time.sleep(1)
            authors.append(driver.find_element_by_xpath('//*[@id="authDetailsNameSection"]/div/div[1]/div[1]/h2').text)

    except:
        err_type = 7
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type
    print(title)
    print(paper_type)
    print(journal)
    print(inst)
    print(vol)
    print(cor_a)
    print(authors)
    print("------------------------------")

    link = driver.current_url
    return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type


#   Scopus는 로그인이 필수. ID, Password를 인자로 받음.
def Scopus_sign_in(ID, Password):
    global driver
    t = 0
    while t < 1:
        t += 1
        try:
            driver.get("https://scopus.com")
            time.sleep(5)
            guest = driver.find_element_by_xpath('//*[@id="_pendo_g_G2mhUNeTB0nRfGXsdP43xf9V25I"]/div/div/table/tbody/tr/td[2]/div/a[2]')
            guest.click()

            time.sleep(5)
            email = driver.find_element_by_xpath('//*[@id="bdd-email"]')
            email.clear()
            #######################################################
            # To use Scopus, you need to sign in. This is my account.
            # write your scopus id
            email.send_keys(ID)
            email.submit()

            time.sleep(5)
            password = driver.find_element_by_xpath('//*[@id="bdd-password"]')
            password.clear()
            # write your scopus password
            password.send_keys(Password)
            signin = driver.find_element_by_xpath('//*[@id="bdd-elsPrimaryBtn"]')
            signin.click()
            #######################################################
        except:
            t -= 1
            
#   DataFrame을 인자로 받고 그에 해당하는 Data 추출. 알 수 없는 error 발생시 selenium initialization이 적용되어있는 함수     
def extract_Scopus_data(df):    
    global driver
    newdf = pd.DataFrame(np.zeros((len(df['제목']), 5)), columns=['Title', 'Link', 'Authors', 'cor_A', 'inst'])

    options = webdriver.ChromeOptions()
    # you have to downloacd chrome driver
    # options.add_argument('headless') --> headless mode
    driver = webdriver.Chrome("D:/chromedriver.exe", options = options)
    
    newdf['Title'] = 'NULL'
    newdf['Link'] = 'NULL'
    newdf['Author'] = 'NULL'
    newdf['cor_A'] = 'NULL'
    newdf['inst'] = 'NULL'
    newdf['vol_num'] = 'NULL'
    newdf['paper_type'] = 'NULL'
    newdf['Journal'] = 'NULL'
    #######################################################
    # you have to input your ID, Password
    Scopus_sign_in("vmfksxp89@gmail.com", "hyojae12!")
    #######################################################
    cnt = 0
    i = -1
    while True:
        try:
            err_cnt = 0
            while i < len(df['제목']) - 1:
                i+= 1
                if i < cnt:
                    continue
                    
                print(str(i) + " : " + df['제목'][i])
                journal, inst, vol, paper_type, title, cor_a, authors, link, err_type = extract_Scopus_title(df['제목'][i])

                if err_type != -1:
                    if err_cnt < 5:
                        i -= 1
                        err_cnt += 1
                        continue
                    else:
                        cnt += 1
                        err_cnt = 0
                        continue
                cnt += 1
                newdf['Journal'][i] = journal
                newdf['inst'][i] = inst
                newdf['vol_num'][i] = vol
                newdf['paper_type'][i] = paper_type
                newdf['Title'][i] = title
                newdf['cor_A'][i] = cor_a
                newdf['Author'][i] = authors
                newdf['Link'][i] = link
            break
        except:
            i -= 1
            selenium_initialize()
            time.sleep(5)
            Scopus_sign_in("vmfksxp89@gmail.com", "hyojae12!")
    return newdf


#  web of science from title
def extract_WOS_title(t, rec_cnt):
    err_type = -1
    journal, inst, vol, paper_type, title, cor_a, authors, link = None, None, None, None, None, None, None, None
    
    driver.get("file:///C:/Users/Haneum/Downloads/WOS_all.html")
    elem = driver.find_element_by_name("value(input2)")
    elem.clear()
    elem.send_keys(t)
    elem.submit()
    driver.switch_to_window(driver.window_handles[1])

    if rec_cnt > 50:
        records = driver.find_element_by_xpath('//*[@id="skip-to-navigation"]/ul[2]/li[3]/a')
        records.click()
        check_all = driver.find_element_by_xpath('//*[@id="selectallTop"]')
        check_all.click()
        remove = driver.find_element_by_xpath('//*[@id="deleteBtm"]')
        remove.click()
        rec_cnt = 0

        driver.close()
        driver.switch_to_window(driver.window_handles[0])

        elem.clear()
        elem.send_keys(t)
        elem.submit()
        driver.switch_to_window(driver.window_handles[1])
    
    # sorting by relativeness
    try:
        relatives = driver.find_element_by_xpath('//*[@id="RS.D;PY.D;AU.A;SO.A;VL.D;PG.A"]')
        relatives.click()
    except:
        print("존재하지 않음. 연관 정렬")
        driver.close()
        driver.switch_to_window(driver.window_handles[0])
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type
    
    # click the link
    try:
        time.sleep(1)
        link = driver.find_element_by_id('RECORD_1')
        link = link.find_element_by_xpath('div[3]/div/div[1]/div/a')
        link.click()
    except:
        print("존재하지 않음.")
        driver.close()
        driver.switch_to_window(driver.window_handles[0])
        return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type

    text = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div').text.split("\n")
    journal = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[3]').text.split("\n")[0]
    cor_a = []
    for i, v in enumerate(text):
        if "출판사" == v:
            inst = text[i + 1]
        if "문서 유형" in v:
            paper_type = v[6:]
        if "논문 번호" in v:
            vol = v.split("논문 번호:")
            vol = vol[len(vol) - 1][1:]
        if "페이지" in v:
            vol = v.split("페이지:")
            vol = vol[len(vol) - 1][1:]
        if "corresponding author" in v:
            cor_a.append(v[6:])
    
    link = driver.current_url
    title = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[1]/value').text
    authors = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[2]/p').text
    authors = authors[3:].split(" ; ")
    for i, v in enumerate(authors):
        authors[i] = authors[i].split("(")[1].split(")")[0]
    driver.close()
    driver.switch_to_window(driver.window_handles[0])
    
    print(title)
    print(paper_type)
    print(journal)
    print(inst)
    print(vol)
    print(cor_a)
    print(authors)
    print("------------------------------")

    return journal, inst, vol, paper_type, title, cor_a, authors, link, err_type
    
#   web of science from DataFrame
def extract_WoS_data(df):
    global driver
    newdf = pd.DataFrame(np.zeros((len(df['제목']), 5)), columns=['Title', 'Link', 'Authors', 'cor_A', 'inst'])
    options = webdriver.ChromeOptions()
    # you have to downloacd chrome driver
    # options.add_argument('headless') --> headless mode
    driver = webdriver.Chrome("D:/chromedriver.exe", options = options)
    
    newdf['Title'] = 'NULL'
    newdf['Link'] = 'NULL'
    newdf['Author'] = 'NULL'
    newdf['cor_A'] = 'NULL'
    newdf['inst'] = 'NULL'
    newdf['vol_num'] = 'NULL'
    newdf['paper_type'] = 'NULL'
    newdf['Journal'] = 'NULL'
    
    cnt = 0
    i = -1
    rec_cnt = 0
    while True:
        try:
            err_cnt = 0
            while i < len(df['제목']) - 1:
                i+= 1  
                if i < cnt:
                    continue
                print(str(i) + " : " + df['제목'][i])
                rec_cnt += 1
                journal, inst, vol, paper_type, title, cor_a, authors, link, err_type = extract_WOS_title(df['제목'][i], rec_cnt)

                if err_type != -1:
                    if err_cnt < 5:
                        i -= 1
                        err_cnt += 1
                        continue
                    else:
                        cnt += 1
                        err_cnt = 0
                        continue
                cnt += 1
                newdf['Journal'][i] = journal
                newdf['inst'][i] = inst
                newdf['vol_num'][i] = vol
                newdf['paper_type'][i] = paper_type
                newdf['Title'][i] = title
                newdf['cor_A'][i] = cor_a
                newdf['Author'][i] = authors
                newdf['Link'][i] = link
            break
        except:
            i -= 1
            try:
                driver.close()
                driver.close()
            except:
                tmp = 0
            selenium_initialize()
            time.sleep(5)
    return newdf


    
def DBpia_title(title):
    base_url = "http://api.dbpia.co.kr/v2/search/search.xml?key=4dd3e593863b69406344f19293f15eff&target=se&searchall=" + title
    req = requests.get(base_url)
    raw = req.text
    
    Link = 'DBpia'
    if "검색결과가 없습니다." in raw:
        return Link, 'NULL', [], 'NULL'
    
    Title = (raw.split("<title>")[1]).split("</title>")[0].replace("&lt;!HE&gt;", "").replace("&lt;!HS&gt;", "")
    if "authors" in raw:
        get_authors = (raw.split("<authors>")[1]).split("</authors>")[0]
        author_pattern = re.findall("<name>.*</name>", get_authors)
        for j, w in enumerate(author_pattern):
            author_pattern[j] = w.replace("<name>", "").replace("</name>", "")
        Authors = author_pattern
    else:
        Authors = []
    
    if "publisher" in raw:
        get_publisher = (raw.split("<publisher>")[1]).split("</publisher>")[0]
        get_publisher = re.findall("<name>.*</name>", get_publisher)[0].replace("<name>", "").replace("</name>", "")
        Publisher = get_publisher
    else:
        Publisher = "NULL"
    return Link, Title, Authors, Publisher
    
    
#df = pd.read_excel("paper.xlsx", sheet_name='Sheet1', header=0, encoding="utf-8")
def DBpia_data(df):
    newdf = pd.DataFrame(np.zeros((len(df['논문제목']), 4)), columns=['Title', 'Link', 'Authors', 'Publisher'])
    cnt = 0;
    
    for i, v in enumerate(df['논문제목']):
        if cnt > i:
            continue
        print(str(i) + " : " + v)
        base_url = "http://api.dbpia.co.kr/v2/search/search.xml?key=4dd3e593863b69406344f19293f15eff&target=se&searchall=" + v
        req = requests.get(base_url)
        raw = req.text
        newdf['Link'][i] = "DBpia"
        if "검색결과가 없습니다." in raw:
            print("검색 결과 없음.")
            newdf['Title'][i] = "NULL"
            cnt += 1
            continue
        newdf['Title'][i] = (raw.split("<title>")[1]).split("</title>")[0].replace("&lt;!HE&gt;", "").replace("&lt;!HS&gt;", "")

        if "authors" in raw:
            get_authors = (raw.split("<authors>")[1]).split("</authors>")[0]
            author_pattern = re.findall("<name>.*</name>", get_authors)
            for j, w in enumerate(author_pattern):
                author_pattern[j] = w.replace("<name>", "").replace("</name>", "")
            newdf['Authors'][i] = author_pattern
        else:
            newdf['Authors'][i] = []
        if "publisher" in raw:
            get_publisher = (raw.split("<publisher>")[1]).split("</publisher>")[0]
            get_publisher = re.findall("<name>.*</name>", get_publisher)[0].replace("<name>", "").replace("</name>", "")
            newdf['Publisher'][i] = get_publisher
        else:
            newdf['Publisher'][i] = "NULL"
        cnt += 1
    newdf['T_val'] = 0
    newdf['A_val'] = 0
    newdf['A_err'] = ""
    newdf['Publisher'] = 0
    newdf['Author_Number_ext'] = 0
    
    newdf['저자목록'] = df['저자목록'].apply(lambda x: x.replace('&', ','))

    for i, v in enumerate(newdf['저자목록']):
        newdf['저자목록'][i] = re.sub('외\s\d+명$', '', newdf['저자목록'][i])
    newdf['저자목록'] = newdf['저자목록'].apply(lambda x: x.split(', '))

    for i, v in enumerate(newdf['저자목록']):
        newdf['저자목록'][i] = [x for x in newdf['저자목록'][i] if x]

    for i, v in enumerate(newdf['저자목록']):
        for j, w in enumerate(newdf['저자목록'][i]):
            newdf['저자목록'][i][j] = re.sub('\s*$', '', newdf['저자목록'][i][j])
            newdf['저자목록'][i][j] = re.sub('^\s*', '', newdf['저자목록'][i][j])
    for i, v in enumerate(newdf['Authors']):
            if str(newdf['Authors'][i]) == "0.0":
                newdf['Authors'][i] = []
    newdf['Author_Number_ext'] = newdf['Authors'].apply(lambda x: len(x))
    newdf['Author_Number_data'] = newdf['저자목록'].apply(lambda x: len(x))
    
    return newdf



def compare_name_string(name, name_list):
	if name_list.count(','):
	    end = name_list.find(',')
	    name_list = name_list[0 : end : ]
	elif name_list.count('，'):
	    end = name_list.find('，')
	    name_list = name_list[0 : end : ]
	return compare_name(name, name_list)



def compare_name(n1, n2):
    n1 = n1.upper()
    n2 = n2.upper()
    n1 = n1.replace('-', ' ')
    n2 = n2.replace('-', ' ')
   
    n1 = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', n1)
    n2 = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', n2)
    n1_list = n1.split(' ')
    n2_list = n2.split(' ')
    flag = False
    if len(n1_list) == 1 and len(n2_list) == 1:
        if n1_list[0] == n2_list[0]:
            return True
        else:
            return False
    for i, v in enumerate(n1_list):
        for j, w in enumerate(n2_list):
            if n1_list[i] == n2_list[j]:
                flag = True
                del n1_list[i]
                del n2_list[j]
                break
        if flag == True:
            break
            
    if flag == True:
        for i, v in enumerate(n1_list):
            for j, w in enumerate(n2_list):
                if v[:1] == w[:1]:
                    return True
    return False


def search_for_coauthor(name, _list):
	if _list.count(','):
	    _list = _list.split(', ')
	    for i in range(1,len(_list)):
	        if compare_name(name, _list[i]):
	            return True
	    return False
	elif _list.count('，'):
	    _list = _list.split('， ')
	    for i in range(1,len(_list)):
	        if compare_name(name, _list[i]):
	            return True
	    return False    
	else:
	    return False

def coauthor_list(name, _list):
    for i in range(1,len(_list)):
        if compare_name(name, _list[i]):
            return True
    return False
		     	


def extract_text_pypdf2(filename):
	pdfFileObj = open(filename,'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	num_pages = pdfReader.numPages
	print('\nNumber of pages: ', num_pages)
	count = 0
	text = ""
	pageObj = pdfReader.getPage(count)
	text += pageObj.extractText()
	if text != "":
		text = text
	else:
		text = textract.process(filename, method='tesseract', language='eng')
	print('-----------------------------PyPDF2-------------------------------------')
	print("\n\n\nextracted text: ")
	print(text)



def collect_keywords(text):
	tokens = word_tokenize(text)
	punctuations = ['(',')',';',':','[',']',',']
	stop_words = stopwords.words('english')
	keywords = [word for word in tokens if not word in stop_words and not word in punctuations]
	return keywords
	#print('\nkeywords: \n')
	#print(keywords)



def validate_journal_doi(doi, keywords):
	doi_result = difflib.get_close_matches(doi.lower(), keywords, cutoff=1)
	doi_result_short = difflib.get_close_matches(doi[10 : len(doi) : ].lower(), keywords, cutoff=1)
	if len(doi_result) != 0 or len(doi_result_short) != 0:
		print("\n\ndoi is validated\t==> ", doi)
	else:
		print("\n\nDoi did NOT match")
		print("Check your doi: ", doi)



def extract_title(text):
	if text == "":
		extracted_title = ""
	else: 
		starting = text.find('>')
		ending = text.find('</a>')
		extracted_title = text[starting+1 : ending : ]
		if extracted_title.count('b>') > 1:
			extracted_title = extracted_title.replace('<b>', '')
			extracted_title = extracted_title.replace('</b>', '')
	return extracted_title



def validate_title(title, text):
	starting = text.find('>')
	ending = text.find('</a>')
	extracted_title = text[starting+1 : ending : ]
	if extracted_title.count('b>') > 1:
		extracted_title = extracted_title.replace('<b>', '')
		extracted_title = extracted_title.replace('</b>', '')
	if title.lower() == extracted_title.lower():
		print('\nTitle is validated\t==> ', extracted_title)
	else:
		print("\nTitle did NOT match")
		print("Check your Title: ", title)



def validate_title_from_pdf(title1, text):
	if fuzz.partial_ratio(title1.lower(), text.lower()) == 100:
		print('\nTitle is validated\t==> ', title1)
	else:
		print("\nTitle did NOT match")
		print("Check your Title: ", title1)



def validate_journal_name(journal_name, text):
	if fuzz.partial_ratio(journal_name.lower(), text.lower()) == 100:
		print('\nJournal name name is validated\t==> ', journal_name)
	else:
		print("\nJournal name name did NOT match")
		print("Check the journal name: ", journal_name)
	print(fuzz.partial_ratio(journal_name.lower(), text.lower()))



def validate_journal_name_keywords(journal_name, keywords):
	keys = [' '.join([i,j]) for i,j in zip(keywords, keywords[1:])]
	journal_result = difflib.get_close_matches(journal_name.lower(), keys, cutoff=1)
	if len(journal_result) != 0:
		print("\nJournal name is validated\t==> ", journal_name)
	else:
		print("\nJournal name did NOT match")
		print("Check the journal name: ", journal_name)



def validate_author_name(author, text):
	shuffle = author.split(' ')
	author_shuffle = ' '.join(reversed(shuffle))
	if fuzz.partial_ratio(author, text) == 100 or fuzz.partial_ratio(author_shuffle, text) == 100:
		return True
	else:
		return False
	#print(fuzz.partial_ratio(author, text))




def validate_author_name_keywords(author, keywords):
	shuffle = author.split(' ')
	author_shuffle = ' '.join(reversed(shuffle))
	keys = [' '.join([i,j]) for i,j in zip(keywords, keywords[1:])]
	author_result = difflib.get_close_matches(author.lower(), keys, cutoff=1)
	author_result2 = difflib.get_close_matches(author_shuffle.lower(), keys, cutoff=1)
	if len(author_result) != 0 or len(author_result2) != 0:
		return True
	else:
		return False



def extract_author_names(text):
	not_full = False
	soup = bs(text, "lxml")
	temp = soup.find('div', 'gs_a').get_text()
	end = temp.find('-')
	all_authors = temp[0 : end-1 : ]
	if all_authors.count('…'):
		all_authors = all_authors.replace('…', ', etc.')
		not_full = True
	return not_full, all_authors
	

def divide_doi(doi):
	#doi_find = [match for match in keywords if "//doi.org" in match]
	#doi_short = doi_find[0][10 : len(doi_find[0]) : ]
	doi_short = doi[10 : len(doi) : ]
	index = doi_short.find('/')
	doi_1 = doi_short[0 : index : ]
	doi_2 = doi_short[index+1 : len(doi_short) : ]
	return doi_1, doi_2


def make_title(title):
	title = title.replace(' ', '+')
	return title

if __name__ == '__main__':
	main()



