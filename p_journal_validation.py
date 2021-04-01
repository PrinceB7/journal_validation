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
	data = pd.read_csv('data1.csv')
	professor = pd.read_csv('professor.csv')
	print(data.values.shape)
	x = data[['key', 'title', 'author_count', 'author_rank', 'author_names']]
	print(x.shape)
	
	#'''
	for ix in range(45, 85):
		sleep_time = random.randint(15,20)
		print('\n', ix, ' - ', x.iloc[ix]['title'], '\n')

		key = x.iloc[ix]['key']
		original_author = professor[professor["키"]==key]
		korean = original_author['국문'].iloc[0]
		english = original_author['영문'].iloc[0]	

		#fist author
		if x.iloc[ix]['author_rank'] == '제1저자':
			print('\nFirst author\n')
			_title, not_full, _authors = google_scholar(x.iloc[ix]['title'])

			if _title == 'empty':
				x.loc[ix, 'val_title'] = 'empty'
				x.to_csv('paper.csv', index=False)
				x.loc[ix, 'val_rank'] = 'empty'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote empty to the file\n')
				continue
			elif _title == 'not_found':
				x.loc[ix, 'val_title'] = 'not_found'
				x.to_csv('paper.csv', index=False)
				x.loc[ix, 'val_rank'] = 'not_found'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote not_found to the file\n')
				continue	

			print(x.iloc[ix]['title'])
			print(korean, ' ; ', english)
			print('\nExtracted title and authors:')
			print(_title)
			print(_authors)
			if difflib.SequenceMatcher(None, x.iloc[ix]['title'].lower(), _title.lower()).ratio()>0.90:
				x.loc[ix, 'val_title'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid title to the file\n')
			else:
				th = "{:.2f}".format(difflib.SequenceMatcher(None, x.iloc[ix]['title'].lower(), _title.lower()).ratio())
				x.loc[ix, 'val_title'] = 'invalid ('+str(th)+')'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid title to the file\n')

			if compare_name_string(korean, _authors) or compare_name_string(english, _authors):
				x.loc[ix, 'val_rank'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid author_name to the file\n')
			else:
				x.loc[ix, 'val_rank'] = 'invalid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid author_name to the file\n')
			time.sleep(sleep_time)

		#co-author	
		elif x.iloc[ix]['author_rank'] == '공동저자':	
			print('\nCo - author\n')
			_title, not_full, _authors = google_scholar(x.iloc[ix]['title'])

			if _title == 'empty':
				x.loc[ix, 'val_title'] = 'empty'
				x.to_csv('paper.csv', index=False)
				x.loc[ix, 'val_rank'] = 'empty'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote empty to the file\n')
				continue
			elif _title == 'not_found':
				x.loc[ix, 'val_title'] = 'not_found'
				x.to_csv('paper.csv', index=False)
				x.loc[ix, 'val_rank'] = 'not_found'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote not_found to the file\n')
				continue		

			print(x.iloc[ix]['title'])
			print(korean, ' ; ', english)
			print('\nExtracted title and authors:')
			print(_title)
			print(_authors)
			if difflib.SequenceMatcher(None, x.iloc[ix]['title'].lower(), _title.lower()).ratio()>0.90:
				x.loc[ix, 'val_title'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid title to the file\n')
			else:
				th = "{:.2f}".format(difflib.SequenceMatcher(None, x.iloc[ix]['title'].lower(), _title.lower()).ratio())
				x.loc[ix, 'val_title'] = 'invalid ('+str(th)+')'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid title to the file\n')

			if search_for_coauthor(korean, _authors) or search_for_coauthor(english, _authors):
				x.loc[ix, 'val_rank'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid author_name to the file\n')
			elif not_full:
				x.loc[ix, 'val_rank'] = 'unknown'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote unknown author_name to the file\n')	
			else:	
				x.loc[ix, 'val_rank'] = 'invalid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid author_name to the file\n')
			time.sleep(sleep_time)

		#corresponding author		
		else:
			print('\nCorresponding author\n')
			_title, not_full, _authors = google_scholar(x.iloc[ix]['title'])

			if _title == 'empty':
				x.loc[ix, 'val_title'] = 'empty'
				x.to_csv('paper.csv', index=False)
				x.loc[ix, 'val_rank'] = 'empty'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote empty to the file\n')
				continue
			elif _title == 'not_found':
				x.loc[ix, 'val_title'] = 'not_found'
				x.to_csv('paper.csv', index=False)
				x.loc[ix, 'val_rank'] = 'not_found'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote not_found to the file\n')
				continue		

			print(x.iloc[ix]['title'])
			print(korean, ' ; ', english)
			print('\nExtracted title and authors:')
			print(_title)
			print(_authors)
			if difflib.SequenceMatcher(None, x.iloc[ix]['title'].lower(), _title.lower()).ratio()>0.90:
				x.loc[ix, 'val_title'] = 'valid'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote valid title to the file\n')
			else:
				th = "{:.2f}".format(difflib.SequenceMatcher(None, x.iloc[ix]['title'].lower(), _title.lower()).ratio())
				x.loc[ix, 'val_title'] = 'invalid ('+str(th)+')'
				x.to_csv('paper.csv', index=False)
				print('\nI wrote invalid title to the file\n')

			x.loc[ix, 'val_rank'] = 'corr_unknown'
			x.to_csv('paper.csv', index=False)

			time.sleep(sleep_time)			




	#'''		




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


def extract_WOS_title(title):
    #######################################################
    driver = webdriver.Chrome("/home/prince/chromedriver")
    #######################################################
    driver.get("file:///home/prince/Lab/journal-validation/api/WOS_all.html")
    elem = driver.find_element_by_name("value(input2)")
    elem.clear()
    elem.send_keys(title)
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
        return 'NULL', 'NULL', [], 'NULL'
    
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
        return 'NULL', 'NULL', [], 'NULL'

    Link = driver.current_url
    Title = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[1]/value').text
    Authors = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[2]/p').text

    try:
        cor_A = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[6]/p[1]').text
    except:
        newdf['cor_A'][i] = 'NULL'
    try:
        inst = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[6]/table[2]').text
    except:
        inst = 'NULL'
        
    driver.close()
    driver.switch_to_window(driver.window_handles[0])
    driver.close()
    
    return Link, Title, Authors, cor_A
    
    
#df = pd.read_excel("paper.xlsx", sheet_name='Sheet1', header=0, encoding="utf-8")
def extract_WoS_data(df):
    newdf = pd.DataFrame(np.zeros((len(df['논문제목']), 5)), columns=['Title', 'Link', 'Authors', 'cor_A', 'inst'])

    options = webdriver.ChromeOptions()
    # you have to downloacd chrome driver
    driver = webdriver.Chrome("/home/prince/chromedriver")
    # WOS api site
    driver.get("file:///home/prince/Lab/journal-validation/api/WOS_all.html")
    
    # this is record of progress. sometimes cause of network error it stops, 
    # then we need to start again from where it stopped
    cnt = 0
    
    newdf['Title'] = 'NULL'
    newdf['Link'] = 'NULL'
    newdf['Author'] = 'NULL'
    newdf['cor_A'] = 'NULL'
    newdf['inst'] = 'NULL'

    driver.switch_to_window(driver.window_handles[0])
    elem = driver.find_element_by_name("value(input2)")
    # this is to delete the search recode. If you do not delete it. Error will occur
    rec_cnt = 0

    for i, v in enumerate(df['논문제목']):
        rec_cnt += 1
        if i < cnt:
            continue
        cnt += 1

        print(str(i) + " : " + v)
        elem.clear()
        elem.send_keys(v)
        elem.submit()
        driver.switch_to_window(driver.window_handles[1])

        if rec_cnt > 50:
            try:
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
                elem.send_keys(v)
                elem.submit()
                driver.switch_to_window(driver.window_handles[1])
            except:
                print("기록 삭제 에러")


        try:
            relatives = driver.find_element_by_xpath('//*[@id="RS.D;PY.D;AU.A;SO.A;VL.D;PG.A"]')
            relatives.click()
        except:
            print("존재하지 않음. 연관 정렬")
            driver.close()
            driver.switch_to_window(driver.window_handles[0])
            continue

        try:
            time.sleep(1)
            link = driver.find_element_by_id('RECORD_1')
            link = link.find_element_by_xpath('div[3]/div/div[1]/div/a')
            link.click()
        except:
            print("존재하지 않음.")
            driver.close()
            driver.switch_to_window(driver.window_handles[0])
            continue

        newdf['Link'][i] = driver.current_url
        Title = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[1]/value').text
        
        newdf['Title'][i] = Title
        print(Title)
        Authors = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[2]/p').text
        newdf['Authors'][i] = Authors
        print(Authors)
        try:
            cor_A = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[6]/p[1]').text
            newdf['cor_A'][i] = cor_A
            print(cor_A)
        except:
            newdf['cor_A'][i] = 'NULL'
            print("교신저자 없음")
        try:
            inst = driver.find_element_by_xpath('//*[@id="records_form"]/div/div/div/div[1]/div/div[6]/table[2]').text
            newdf['inst'][i] = inst
            print(inst)
        except:
            print('기관 없음')

        driver.close()
        driver.switch_to_window(driver.window_handles[0])
        
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



