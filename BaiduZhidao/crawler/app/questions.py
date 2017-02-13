# -*- coding:utf-8 -*-
__author__ = 'xwk'
"""
    通过URL去爬单个的问题
    百度页面的加载 需要用到 js
"""
import threading
import requests
from bs4 import BeautifulSoup

from dataBase.redis_base import get_db_pipeline
from settings import REDIS_PORT, REDIS_HOST, REDIS_DONE_URL_TB
from zhidao_obj import Comment
from dataBase.xml_store_zhidao import Converter

lock = threading.Lock()
class Question:
    def __init__(self, url):
        self.url = url

    @staticmethod
    def get_url():
        redis_pipeline = get_db_pipeline(REDIS_HOST, REDIS_PORT)
        print redis_pipeline.smembers('baiDuZhiDao_ID').execute()

    @staticmethod
    def set_url(url):
        redis_pipeline = get_db_pipeline(REDIS_HOST, REDIS_PORT)
        lock.acquire()
        redis_pipeline.sadd(REDIS_DONE_URL_TB, url).execute()
        lock.release()

    @staticmethod
    def get_done_url_num():
        redis_pipeline = get_db_pipeline(REDIS_HOST, REDIS_PORT)
        lock.acquire()
        num = redis_pipeline.scard(REDIS_DONE_URL_TB).execute()
        lock.release()
        return num

    @staticmethod
    def mul_get_url():
        redis_pipeline = get_db_pipeline(REDIS_HOST, REDIS_PORT)
        lock.acquire()
        # 取出4条数据
        url_list = []
        num = 10
        while num > 0:
            url = redis_pipeline.spop('baiDuZhiDao_URL').execute()
            if len(url) > 0:
                url_list.append(url[0])
            num -= 1
        lock.release()
        return url_list

    @staticmethod
    def get_question(url):
        from selenium import webdriver
        driver = webdriver.PhantomJS()
        # 网页url链接失效了
        try:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            question = soup.find_all('title')[0].get_text()
            Keywords = soup.find_all('meta', {'name': 'keywords'})[0].get('content')
            Description = soup.find_all('meta', {'name': 'description'})[0].get('content')
        except:
            print "链接失效"
            pass

        # 可能没有最佳答案
        try:
            BestAnswer = soup.find_all('div', {'class': 'bd answer'})
            best_qRA_list = best_aRA_list = []
            for qRA in BestAnswer[0].find_all('pre', {'accuse': 'qRA'}):
                best_qRA_list.append(qRA.get_text())
            for aRA in BestAnswer[0].find_all('pre', {'accuse': 'aRA'}):
                best_aRA_list.append(aRA.get_text())
            BestAnswer = BestAnswer[0].find_all('pre', {'accuse': 'aContent'})[0].get_text()
        except:
            pass

        try:
            # 展开所有的回答
            elem = driver.find_element_by_id('show-answer-hide')
            elem.click()
            import time
            time.sleep(10)
        except:
            pass

        #Answers = soup.find_all('div', {'answer-text line'})
        Answers = soup.find_all('div', {'answer'})
        Answers_list = []
        for answer in Answers:
            try:
                qRA_list = aRA_list =[]
                con = answer.find_all('span', {'class': 'con'})[0].get_text()
                qRA = answer.find_all('pre', {'accuse': 'qRA'})
                for temp in qRA:
                    qRA_list.append(temp.get_text())
                aRA = answer.find_all('pre', {'accuse': 'aRA'})
                for temp in aRA:
                    aRA_list.append(temp.get_text())
                Answers_list.append((con, qRA_list, aRA_list))
            except:
                pass
        # 获取当前已爬url的数量
        ID = int(Question.get_done_url_num()[0]) + 1
        # 保存数据
        Converter.save_xml(
            Comment(ID, question, Description, Keywords, BestAnswer, best_qRA_list, best_aRA_list, Answers_list))
        # 将url保存到已爬队列中
        Question.set_url(url)

if __name__ == '__main__':
    #print Question.get_url()
    #print Question.mul_get_url()
    #url = "https://zhidao.baidu.com/question/2075918943425977948.html?qbl=relate_question_1"
    #proxy = 'http://111.120.149.241:9999'

    import time
    start = time.time()
    url_list = Question.mul_get_url()
    for url in url_list:
        print url[0]
        Question.get_question(url[0])
    end = time.time()
    print end-start

    #url = 'http://zhidao.baidu.com/question/1822698985694405028.html?fr=qlquick&entry=qb_list_default'
    #Question.get_question(url, 2)
