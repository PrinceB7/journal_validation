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




def main():
	#getting data from a file
	
	data = pd.read_csv('title_page.csv')
	#id, number, title, form, date, publisher
	x = data[['사번', '연번', '저서명(원어)', '저서형태', '출판년월', '출판사']]

	#read author count page here
	c = pd.read_csv('count_page.csv')

	#read extracted data here
	s = pd.read_csv('authors_val_h.csv')
	#'''
	for ix in range(0, 187):
		print("Now doing row number: ", ix)


		#checking

		if s.iloc[ix]['저서명(원어)'] == '0':
			print('unknown')
			x.loc[ix, 'val_title'] = 'unknown'
			x.loc[ix, 'val_저서형태'] = 'unknown'
			x.loc[ix, 'val_출판년월'] = 'unknown'
			x.loc[ix, 'val_출판사'] = 'unknown'
			#x.loc[ix, 'val_author'] = 'unknown'
			x.loc[ix, 'val_author_number'] = 'unknown'
			continue	
		
		title = s.iloc[ix]['저서명(원어)']
		#author = s.iloc[ix]['발명자이름']
		#author_list = author.split(", ")

		or_title = x.iloc[ix]['저서명(원어)']
		ind = or_title.find(": ")
		or_title2 = or_title[0: ind : ]

		
		#ins 1: validating the title of the patent
		if title in or_title:
			x.loc[ix, 'val_title'] = 'valid'
		elif difflib.SequenceMatcher(None, or_title.lower(), title.lower()).ratio()>=0.85:
			x.loc[ix, 'val_title'] = 'valid'
		elif difflib.SequenceMatcher(None, or_title2.lower(), title.lower()).ratio()>=0.85:
			x.loc[ix, 'val_title'] = 'valid'
		else:
			th = "{:.2f}".format(difflib.SequenceMatcher(None, or_title.lower(), title.lower()).ratio())
			x.loc[ix, 'val_title'] = 'invalid ('+str(th)+')'


			
		#ins 2: validating 저서형태 column (0 or not)
		if s.iloc[ix]['저서형태'] == '0':
			if '초판' in x.iloc[ix]['저서형태']:
				x.loc[ix, 'val_저서형태'] = 'valid'
			else:
				x.loc[ix, 'val_저서형태'] = 'invalid'
		else:
			if '개정' in x.iloc[ix]['저서형태']:
				x.loc[ix, 'val_저서형태'] = 'valid'
			else:
				x.loc[ix, 'val_저서형태'] = 'invalid'		
		


		#ins 3: validating date
		if str(x.iloc[ix]['출판년월']) in str(s.iloc[ix]['출판년월']):
			x.loc[ix, 'val_출판년월'] = 'valid'
		else:
			x.loc[ix, 'val_출판년월'] = 'invalid'


		
		#ins 4: validating publisher
		if x.iloc[ix]['출판사'] in s.iloc[ix]['출판사'] or s.iloc[ix]['출판사'] in x.iloc[ix]['출판사']:
			x.loc[ix, 'val_출판사'] = 'valid'
		elif difflib.SequenceMatcher(None, x.iloc[ix]['출판사'].lower(), s.iloc[ix]['출판사'].lower()).ratio()>=0.70:
			x.loc[ix, 'val_출판사'] = 'valid'
		else:
			th = "{:.2f}".format(difflib.SequenceMatcher(None, x.iloc[ix]['출판사'].lower(), s.iloc[ix]['출판사'].lower()).ratio())
			x.loc[ix, 'val_출판사'] = 'invalid ('+str(th)+')'

		
		#ins 5: this is done below



		#ins 6: counting the author number
		s_count = s.iloc[ix]['Author_Number']	
		x_id = x.iloc[ix]['사번']
		x_num = x.iloc[ix]['연번']
		sss = c[(c["사번"]==x_id) & (c["논문연번"]==x_num)]
		x_count = len(sss)
		if s_count == x_count:
			x.loc[ix, 'val_author_number'] = 'valid'
		else:
			x.loc[ix, 'val_author_number'] = 'invalid'


		x.to_csv('new_patent.csv', encoding = 'utf-8-sig', index=False)

	print('\n\nDone------------\n\n')
	#'''



	#Ins 5: validating main author
	#'''
	nj = 0
	x2 = pd.read_csv('new_patent.csv')
	for iy in range(0, 1858):
		print("Now doing row number: ", iy)
		if c.iloc[iy]['교수본인'] == 'Y':
			c_id = c.iloc[iy]['사번']
			c_num = c.iloc[iy]['논문연번']
			or_author = c.iloc[iy]['저자명']
			#print(or_author)
			sss = s[(s["사번"]==c_id) & (s["연번"]==c_num)]

			if or_author in sss['Author'].iloc[0]:
				x2.loc[nj, 'val_main_author'] = 'valid '
			elif sss['Author'].iloc[0] == '0':
				x2.loc[nj, 'val_main_author'] = 'unknown '
			else: 
				x2.loc[nj, 'val_main_author'] = 'invalid '
			nj += 1	

		x2.to_csv('new_patent.csv', encoding='utf-8-sig', index=False)		
	
	#'''

	
	
	

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

	viewbox = driver.find_element_by_class_name('gs_or_cit')
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
	if index != -1:
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



