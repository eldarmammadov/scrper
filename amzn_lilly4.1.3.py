from random import choice,choices

from tkinter import *
from tkinter import simpledialog

import pandas as pd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import DesiredCapabilities

import time
import sys,os

def random_color_code():
    hex_chars=['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    hex_code='#'
    for i in range(0,6):
        hex_code=hex_code+choice(hex_chars)
    return '#' + ''.join(choices(hex_chars, k = 6))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

#reading from csv file url-s
def readCSV(path_csv):
    df=pd.read_csv(path_csv)
    return df

fileCSV=readCSV(resource_path('./urls.csv'))
print((resource_path('./urls.csv')))
length_of_column_urls=fileCSV['linkamazon'].last_valid_index()

def create_driver():
    chrome_options = Options()

    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"

    chrome_options.headless = True
    chrome_options.add_argument("start-maximized")
    #chrome_options.add_argument("window-size=1400,600")
    #chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    webdriver_service = Service(resource_path('./driver/chromedriver.exe'))
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options, desired_capabilities=caps)
    print("Headless Chrome Initialized")
    print(driver.get_window_size())
    driver.set_window_size(1920, 1080)
    size = driver.get_window_size()
    print("Window size: width = {}px, height = {}px".format(size["width"], size["height"]))

    return driver

#creating main window
window=Tk()
window.geometry('%dx333+0+%d'%(window.winfo_screenwidth(),window.winfo_screenheight()/3))
window.title('amazon_scraper')
#creating string variable which will change every time pages are been scraped
var_pg=StringVar()
###var_pg.set('Page 001 placeholder')
#class of custom labels for pages
class lbl_custom(Label):
    def __init__(self,frame_window):
        super().__init__(frame_window)
        self['width']=33
        self['font']='Segoe 12'
        self['anchor']='w'

#creating frames for two separate
fr_submit_entry_url=Frame(window)
fr_pages=Frame(window)

lbl_url=Label(fr_submit_entry_url,width=33,text='URL',font='Segoe 12 bold')
lbl_question_pages=Label(fr_submit_entry_url,width=33,text='How many pages to be scraped?',font='Segoe 12 bold')
#creating variable for url that would be taken from csv file
var_url=StringVar()
#craeting entry for input value of pages value
entry_value_pg=Entry(fr_submit_entry_url)

#going to urls 1-by-1
def goToUrl_Se(driver):
    global counter
    counter = 0
    for j in range(0, length_of_column_urls + 1):
        xUrl = fileCSV.iloc[j, 1]
        print(xUrl,j)
        var_url.set(xUrl)
        window.update()
        # going to url(amazn) via Selenium WebDriver
        driver.get(xUrl)
        #show pages num
        ##time.sleep(33)
        wait = WebDriverWait(driver, timeout=77)
        count_of_pages=wait.until(EC.visibility_of_element_located((By.XPATH,'//span[@class="s-pagination-strip"]/span[last()]')))#driver.find_element(By.XPATH,'//span[@class="s-pagination-strip"]/span[last()]')
        how_many_pages_in_val=simpledialog.askinteger("Pages to be scraped", "Enter number of pages to be scraped:", parent=window)#entry_value_pg.get()
        i_pages_to_scrpe=int(how_many_pages_in_val)
        if i_pages_to_scrpe>1:
            for i in range(1,i_pages_to_scrpe+1):
                # continue on if there is more pages to load and scrape
                # call again parse data--! going to next page should be before loop occurs to next line in csv
                wait = WebDriverWait(driver, timeout=33)
                parse_data()
                a=str(i+1)
                print(a)
                locator='//a[@aria-label="Go to page '+a+'"]'
                print('go to {}'.format(a))
                wait.until(EC.visibility_of_element_located((By.XPATH, locator))).click()
                lbl_pg00['text'] = 'Page  ' + str(i) + '  has been scraped'
                window.update()
        else:
            parse_data()
        lbl_pg01['text'] = 'Link  ' + str(j+1) + '  has been scraped'
        window.update()
        counter += 1
    lbl_pg03['text'] = 'Close application and check file'
    window.update()
    driver.quit()

###var_url.set('w..amazn')
lbl_URL=Label(fr_submit_entry_url,textvariable=var_url,font='Segoe 9')
driver=create_driver()
def get_value_enrty():
    goToUrl_Se(driver)
    return entry_value_pg.get()

#creating button widget for submit(running) scrape function
btn_submit=Button(fr_submit_entry_url,text='Scrape',font='Segoe 12',command=get_value_enrty,width='33',relief=RAISED)

#placing frames on main window
fr_submit_entry_url.grid(row=0,column=0)
fr_pages.grid(row=1,column=0)
#placing widgets onframe submit url entry
lbl_url.grid(row=0,column=0)
#lbl_question_pages.grid(row=1,column=0)
lbl_URL.grid(row=0,column=1)
#entry_value_pg.grid(row=1,column=1)
btn_submit.grid(row=2,column=0)

#fetch-parse the data from url page
def parse_data():
    global title_list, bookform_list, priceNewProd_list,author_list,data_asins_list,isbn13_list,isbn10_list,img_list,url_list,descpt_list
    wait=WebDriverWait(driver,timeout=77)

    title_list=[]
    data_asins_list = []
    author_list=[]
    priceNewProd_list=[]
    bookform_list=[]
    isbn13_list=[]
    isbn10_list=[]
    img_list=[]
    url_list=[]
    descpt_list=[]

    try:
        time.sleep(33)
        x_indexes=wait.until(EC.visibility_of_all_elements_located((By.XPATH,'//div[@data-asin]')))#visibility_of_all_elements_located((By.XPATH,'//div[@data-asin]')))
        print(len(x_indexes),'x_indexes')
    except:
        y_indexes = driver.find_elements(By.XPATH, '//div[@data-asin]')
        print(len(y_indexes))

    counter=1
    for i in range(len(x_indexes)):
        x_indexes = wait.until(EC.visibility_of_all_elements_located((By.XPATH, '//div[@data-asin]')))
        x_data_asin=x_indexes[i].get_attribute('data-asin')
        if x_data_asin!="":
            print(x_data_asin,i,counter)
            data_asins_list.append(x_data_asin)
            counter+=1

            #data-asin <div index blocks
            locator='//div[@data-asin="'+x_data_asin+'"]'
            x_block_of_index=driver.find_element(By.XPATH,locator)

            #locating title
            y_title=x_block_of_index.find_element(By.XPATH,'.//div/h2/a/span')
            varTitle=y_title.text
            title_list.append(varTitle)
            print(varTitle)
            lbl_pgbase['text'] = '.'
            window.update()

            #locating author
            x_author=x_block_of_index.find_element(By.XPATH,".//span[text()='by ']/following-sibling::*[self::span | self::a]")
            author_list.append(x_author.text)
            print(x_author.text)
            lbl_pgbase['text'] = '. .'
            window.update()

            #locating price
            x_price=x_block_of_index.find_element(By.XPATH,'.//span[@class="a-offscreen"]')
            priceNewProd_list.append(x_price.get_attribute('textContent'))
            print(x_price.text)
            lbl_pgbase['text'] = '. . .'
            window.update()

            #locate bookform
            x_bookform=driver.find_element(By.XPATH,'.//span[contains(text(),"Paperback")]')
            bookform_list.append(x_bookform.text)
            print(x_bookform.text)
            lbl_pgbase['text'] = '. . .scraping'
            window.update()

            #clicking to each item for getting isbn values ->back page
            a_href_element_of_index=x_block_of_index.find_element(By.XPATH,'.//h2/a')
            print(a_href_element_of_index)
            lbl_pgbase['text'] = '. . .scraping.'
            window.update()

            a_href_element_of_index.click()
            print('a href page clicked')
            lbl_pgbase['text'] = '. . .scraping. .'
            window.update()
            try:
                a_isbn_element=wait.until(EC.presence_of_all_elements_located((By.XPATH,'//span[contains(@class,"isbn")]/parent::node()/following-sibling::div/span')))

                if len(a_isbn_element)>1:
                    isbn10=a_isbn_element[0].get_attribute('textContent')
                    isbn13=a_isbn_element[1].get_attribute('textContent')
                    isbn10_list.append(isbn10)
                    isbn13_list.append(isbn13)
                else:
                    isbn13 = a_isbn_element[0].get_attribute('textContent')
                    isbn13_list.append(isbn13)
                    isbn10_list.append('')

            except:
                isbn10_list.append('')
                isbn13_list.append('')

            x_img=driver.find_element(By.XPATH,'//img')
            img=x_img.get_attribute('src')
            img_list.append(img)
            page_url=driver.current_url
            print(page_url,'page clicked')
            url_list.append(page_url)

            x_descr=wait.until(EC.presence_of_all_elements_located((By.XPATH,'//div[@data-a-expander-name="book_description_expander"]//span')))
            descr_temp_loop_list=[]
            try:
                for i in range(len(x_descr)):
                    descr_temp_loop_list.append(x_descr[i].text)
                    #inside this iteration results must be joined
                    #final result should be one str value
                    #that will be appended to descrp_list
                    descr_str=' '.join(descr_temp_loop_list)
            except:
                print(x_descr[i].get_attribute('innerHTML'))
            descpt_list.append(descr_str)
            lbl_pgbase['text'] = '. . .scraping. . .'
            window.update()

            driver.execute_script('window.history.go(-1)')

    dict={
        'Asins':data_asins_list,
        'Title':title_list,
        'Author':author_list,
        'Price':priceNewProd_list,
        'Bookform': bookform_list,
        'ISBN13': isbn13_list,
        'ISBN10':isbn10_list,
        'Image URL':img_list,
        'Url':url_list,
        'Description':descpt_list
    }
    df=pd.DataFrame(dict)
    print(df)
    write_to_csv(df)

def write_to_csv(dataframe_var):
    dataframe_var.to_csv('./result01.csv', index=False, header=True,mode='a')
    print('written to csv')
    lbl_pg02['text'] = 'Has written to CSV'
    window.update()

#goToUrl_Se(driver)
#labels for pages
lbl_pg00=lbl_custom(fr_pages)
lbl_pg00.grid(row=1,column=0)
lbl_pg01=lbl_custom(fr_pages)
lbl_pg01.grid(row=2,column=0)
lbl_pg02=lbl_custom(fr_pages)
lbl_pg02.grid(row=3,column=0)
lbl_pg03=lbl_custom(fr_pages)
lbl_pg03.grid(row=4,column=0)
lbl_pgbase=lbl_custom(fr_pages)
lbl_pgbase['fg']=random_color_code()
lbl_pgbase.grid(row=0,column=0)

def opening_showing():
        xUrl = fileCSV.iloc[0, 1]
        var_url.set(xUrl)
        window.update()

opening_showing()
window.mainloop()
#pyinstaller -F --add-data "./urls.csv;./" amzn_lilly4.1.2.py --onefile --clean --add-binary "./driver/chromedriver.exe;./driver"