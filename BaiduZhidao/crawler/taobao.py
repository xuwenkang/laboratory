# -*- coding:utf-8 -*-
__author__ = 'xuwenkang'
from selenium import webdriver
import urllib2
from bs4 import BeautifulSoup
import sys
default_encoding = 'gbk'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
class TaobaoMM:
    def __init__(self):
        self.driver = webdriver.PhantomJS

    def get_page(self):
        USER_AGENT='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36'
        headers = {'User-Agent':USER_AGENT }

        url = "https://zhidao.baidu.com/list?fr=daohang"
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        html = response.read().decode('gbk').encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        print soup
        for title in soup.findAll('div', {'class': 'question-title'}):
            #print title
            pass

if __name__ == "__main__":
    taobaoMM = TaobaoMM()
    taobaoMM.get_page()

