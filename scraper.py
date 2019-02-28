import os
import re
import sys
import shutil
import multiprocessing
from multiprocessing.dummy import Pool
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from time import sleep
from dircreator import DirCreator

sleeper = 1

class Scraper():
    def __init__(self):
        new_dir = DirCreator()
        new_dir.createFolder()
        self.path_dir = new_dir.changeDirectory()

        self.s = 1

        self.drivers = []
        self.text = []
        self.driver = None

    def setUpScrapers(self):
        self.__initDrivers()
        sleep(self.s+2)
        pg_nums = self.driver.find_elements_by_xpath('//a[@class="dxp-num"]')
        num = 1
        for i in range(0, len(pg_nums)):
            self.__initDrivers()
            sleep(self.s+2)
            self.driver.find_element_by_xpath('//a[contains(text(),"{}")]'.format(num + 1)).click()
            if num <= len(pg_nums):
                num += 1

    def __initDrivers(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # options.add_argument('--ignore-certificate-errors')
        # options.add_argument('--test_type')
        plugs = {"enabled":False,"name":"Chrome PDF Viewer"}
        prefs = {"download.default_directory": self.path_dir, "plugins.plugins_list": [plugs]}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.southtechhosting.com/SanJoseCity/CampaignDocsWebRetrieval/Search/SearchByElection.aspx")
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'ctl00_DefaultContent_ASPxRoundPanel1_btnFindFilers_CD')))
        except TimeoutException:
            print("Loading took too long.")

        self.__clickSubmitButton(self.driver)
        self.drivers.append(self.driver)

    def startScrapers(self):
        p = Pool(multiprocessing.cpu_count()-1)
        p.map(self.__iterForms,self.drivers)


    def __iterForms(self,driver):
        forms = driver.find_elements_by_xpath('//a[@class="dxbButton_Glass dxgvCommandColumnItem_Glass dxgv__cci dxbButtonSys"]')
        sleep(self.s)
        top_form_xpath = driver.find_elements_by_xpath('//tr[@class="dxgvDataRow_Glass"]')
        bottom_form_xpath = driver.find_elements_by_xpath('//tr[@class="dxgvDataRow_Glass dxgvLVR"]')
        data = [row for row in top_form_xpath]
        if bottom_form_xpath:
            data.append(bottom_form_xpath[0])
        data_text = [info.text for info in data]

        for ind, form in enumerate(forms):
            sleep(self.s + 1)
            forms = driver.find_elements_by_xpath('//a[@class="dxbButton_Glass dxgvCommandColumnItem_Glass dxgv__cci dxbButtonSys"]')
            forms[ind].click()
            sleep(self.s + 1)
            driver.find_elements_by_xpath('//table[@class="dxgvControl_Glass dxgv"]')
            self.__downloadExcel(driver)
            self.__downloadPdfs(driver)

            self.__orgFiles(ind,data_text)

            # Go back a page
            self.__clickBackButton(driver)
            sleep(self.s)


    def __orgFiles(self,ind,text):
        # create new folder for storing pdfs/excel files for certain group
        raw_str = text[ind]
        new_path = self.path_dir
        clean_str = re.sub('[^A-Za-z0-9]+', '', raw_str)[:175].lower()
        add_new_folder = os.path.join(new_path, clean_str)

        if not os.path.exists(add_new_folder):
            os.makedirs(add_new_folder)

        root_dst_dir = add_new_folder
        files = [f for f in os.listdir(new_path) if os.path.isfile(os.path.join(new_path, f))]
        for file in files:
            shutil.move(os.path.join(new_path, file), root_dst_dir)

    def __clickSubmitButton(self,driver):
        driver.find_element_by_xpath('//*[@id="ctl00_DefaultContent_ASPxRoundPanel1_btnFindFilers_CD"]').click()

    def __clickBackButton(self,driver):
        if driver.find_elements_by_xpath('//*[@id="ctl00_DefaultContent_buttonBack"]'):
            driver.find_elements_by_xpath('//*[@id="ctl00_DefaultContent_buttonBack"]')[0].click()
        else:
            driver.find_elements_by_xpath('//*[@id="ctl00_DefaultContent_buttonBack_CD"]')[0].click()

    def __downloadCheck(self):
        for i in os.listdir(self.path_dir):
            if ".crdownload" in i:
                sleep(0.5)
                self.__downloadCheck()

    def __downloadExcel(self,driver):
        excel = driver.find_elements_by_xpath('//td[@class="dxgvCommandColumn_Glass dxgv"]//img[@title="Export Transaction Details To Excel"]')
        sleep(self.s+1)
        for exfile in excel:
            exfile.click()
        sleep(self.s+1)

    def __downloadPdfs(self,driver):
        pdfs = driver.find_elements_by_xpath('//td[@class="dxgvCommandColumn_Glass dxgv"]//img[@title="View Form"]')
        for pdf_ind in range(0,len(pdfs)):
            driver.find_elements_by_xpath('//td[@class="dxgvCommandColumn_Glass dxgv"]//img[@title="View Form"]')[pdf_ind].click()
            sleep(self.s+2)

            # switch to pdf window
            driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
            delay = 10
            try:
                WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.LINK_TEXT,"Click here")))
            except TimeoutException:
                print("Loading took too much time...")

            a = driver.find_element_by_link_text("Click here")
            ActionChains(driver).key_down(Keys.CONTROL).click(a).key_up(Keys.CONTROL).perform()
            sleep(self.s+2)
            driver.switch_to.default_content()
            driver.find_elements_by_xpath("//div[@id='ctl00_GenericPopupSizeable_InnerPopupControl_PWH-1']")[0].click()
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            self.__downloadCheck()
            sleep(self.s+2)

s = Scraper()
s.setUpScrapers()
s.startScrapers()
'''
Grab all page links on bottom (9) and store in a list (inside Scraper() class)
Have scraper class just pull info from each individual page (don't worry about while loops)
Create a new instance of Scraper() for each page
Use threading/parallel programming for each instance of Scraper() --> run 9 scrapers simultaneously

Need to update pdf downloader to work with FireFox
Need to rework the auto downloader to automatically download files to data folder (files are not downloading into respective
folder, need to make it so files download to the right folder after downloading fully)
'''
