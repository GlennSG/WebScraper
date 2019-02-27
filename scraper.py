import os
import re
import sys
import shutil
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
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

        # options = Options()
        # options.add_argument('headless')
        # options.add_argument('--ignore-certificate-errors')
        # options.add_argument('--test_type')
        # plugs = {"enabled":False}
        # prefs = {"download.default_directory":path_dir,"plugins.plugins_list":[plugs]}
        #options.add_experimental_option("prefs",prefs)
        self.driver = Firefox()

    def start(self):
        self.driver.get("https://www.southtechhosting.com/SanJoseCity/CampaignDocsWebRetrieval/Search/SearchByElection.aspx")
        try:
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.ID,'ctl00_DefaultContent_ASPxRoundPanel1_btnFindFilers_CD')))
        except TimeoutException:
            print("Loading took too long.")

        self.__clickSubmitButton()
        forms = self.__selectFormItems()
        sleep(self.s)
        self.__extractFormText()

        for ind,form in enumerate(forms):
            sleep(self.s+1)
            self.__selectFormItems()
            forms[ind].click()
            sleep(self.s+1)

            next_form = self.__selectNextPageFormItems()
            self.downloadExcel()
            self.downloadPdfs()

            # create new folder for storing pdfs/excel files for certain group
            raw_str = outer_form_text[ind]
            clean_str = re.sub('[^A-Za-z0-9]+','',raw_str)[:175].lower()
            add_new_folder = os.path.join(new_path,clean_str)

            if not os.path.exists(add_new_folder):
                os.makedirs(add_new_folder)

            # move files to new folder
            root_src_dir = new_path
            root_dst_dir = add_new_folder
            files = [f for f in listdir(new_path) if isfile(join(new_path,f))]
            for file in files:
                shutil.move(os.path.join(new_path,file), root_dst_dir)

            # Go back a page
            self.__clickBackButton()
            sleep(self.s)

    def clickSubmitButton(self):
        self.driver.find_element_by_xpath('//*[@id="ctl00_DefaultContent_ASPxRoundPanel1_btnFindFilers_CD"]').click()

    def __clickBackButton(self):
        if driver.find_elements_by_xpath('//*[@id="ctl00_DefaultContent_buttonBack"]'):
            driver.find_elements_by_xpath('//*[@id="ctl00_DefaultContent_buttonBack"]')[0].click()
        else:
            driver.find_elements_by_xpath('//*[@id="ctl00_DefaultContent_buttonBack_CD"]')[0].click()

    def __escape(self):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def __grabText(self,top_form_xpath,bottom_form_xpath):
        data = [row for row in top_form_xpath].append(bottom_form_xpath[0])
        data_text = [info.text for info in data]
        return data_text

    def selectPageNumbers(self):
        return self.driver.find_elements_by_xpath('//a[@class="dxp-num"]')
    def __selectFormItems(self):
        return self.driver.find_elements_by_xpath('//a[@class="dxbButton_Glass dxgvCommandColumnItem_Glass dxgv__cci dxbButtonSys"]')

    def __selectNextPageFormItems(self):
        return self.driver.find_elements_by_xpath('//table[@class="dxgvControl_Glass dxgv"]')

    def __selectExcelElements(self):
        return self.driver.find_elements_by_xpath('//td[@class="dxgvCommandColumn_Glass dxgv"]//img[@title="Export Transaction Details To Excel"]')

    def __selectPdfElements(self):
        return self.driver.find_elements_by_xpath('//td[@class="dxgvCommandColumn_Glass dxgv"]//img[@title="View Form"]')

    def __selectHeadingBar(self):
        driver.find_elements_by_xpath("//div[@id='ctl00_GenericPopupSizeable_InnerPopupControl_PWH-1']")[0].click()

    def __extractFormText(self):
        top_table_row = self.driver.find_elements_by_xpath('//tr[@class="dxgvDataRow_Glass"]')
        bottom_table_row = self.driver.find_elements_by_xpath('//tr[@class="dxgvDataRow_Glass dxgvLVR"]')
        table_text = self.__grabText(top_table_row,bottom_table_row)

    def __switchFrames(self):
        driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))

    def __pdfAction(self):
        ActionChains(driver).key_down(Keys.CONTROL).click(a).key_up(Keys.CONTROL).perform()

    def downloadCheck(self):
        for i in os.list_dir(self.path_dir):
            if ".crdownload" in i:
                sleep(0.5)
                downloadCheck()
    def downloadExcel(self):
        excel = self.__selectExcelElements()
        sleep(self.s+1)
        for exfile in excel:
            exfile.click()
        sleep(self.s+1)

    def downloadPdfs(self):
        pdfs = self.__selectPdfElements()
        for pdf_ind in range(0,len(pdfs)):
            pdfs[pdf_ind].click()
            sleep(self.s+2)

            # switch to pdf window
            self.__switchFrames()
            delay = 10
            try:
                WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.LINK_TEXT,"Click here")))
            except TimeoutException:
                print("Loading took too much time...")

            a = driver.find_element_by_link_text("Click here")
            self.__pdfAction()
            sleep(self.s+2)
            driver.switch_to.default_content()
            self.__selectHeadingBar()
            self.__escape()
            self.downloadCheck()
            sleep(self.s+2)

driver = Firefox()
#s.start()
driver.get("https://www.southtechhosting.com/SanJoseCity/CampaignDocsWebRetrieval/Search/SearchByElection.aspx")
try:
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,'ctl00_DefaultContent_ASPxRoundPanel1_btnFindFilers_CD')))
except TimeoutException:
    print("Loading took too long.")
driver.find_element_by_xpath('//*[@id="ctl00_DefaultContent_ASPxRoundPanel1_btnFindFilers_CD"]').click()
num_list = driver.find_elements_by_xpath('//a[@class="dxp-num"]')
print(num_list)
'''
Grab all page links on bottom (9) and store in a list (inside Scraper() class)
Have scraper class just pull info from each individual page (don't worry about while loops)
Create a new instance of Scraper() for each page
Use threading/parallel programming for each instance of Scraper() --> run 9 scrapers simultaneously
'''
