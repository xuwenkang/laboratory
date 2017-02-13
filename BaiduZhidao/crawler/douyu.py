# -*- coding:utf-8 -*-
__author__ = 'xuwenkang'
from bs4 import BeautifulSoup
import urllib2
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Douyu:

    def __init__(self):
        self.driver = webdriver.PhantomJS()

    def testEle(self):
        driver = self.driver
        driver.get('http://www.douyu.com/directory/all')
        soup = BeautifulSoup(driver.page_source, 'xml')
        while True:
            titles = soup.find_all('h3', {'class': 'ellipsis'})
            nums = soup.find_all('span', {'class': 'dy-num fr'})
            for title, num in zip(titles, nums):
                print title.get_text(), num.get_text()
            if driver.page_source.find('shark-pager-disable-next') != -1:
                break
            # 模拟点击下一页
            elem = driver.find_element_by_class_name('shark-pager-next')
            elem.click()
            soup = BeautifulSoup(driver.page_source, 'xml')

    def tearDown(self):
        print 'down'

if __name__ == "__main__":
    crawler = Douyu()
    crawler.testEle()