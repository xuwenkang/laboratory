# -*- coding:utf-8 -*-
__author__ = 'xuwenkang'
import time

from bs4 import BeautifulSoup
from selenium import webdriver

#from zhidao_obj import ZhidaoObj


class BaiduZhidaoCrawler():

    def __init__(self):
        self.driver = webdriver.PhantomJS()
        from dataBase import redis_base
        from settings import REDIS_PORT, REDIS_HOST
        self.pipeline = redis_base.get_db_pipeline(REDIS_HOST, REDIS_PORT)

        from dataBase import mongo_base
        self.db = mongo_base.get_mongodb_instance('baiduZhiDao')

    # 获取页面
    def get_home_page(self):
        driver = self.driver
        driver.get('https://zhidao.baidu.com/list?cid=101')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        self.handle_page_info(soup)
        while True:
            # 出现 pTag next disabled 意味着已经到了最后一页
            if driver.page_source.find('pTag next disabled') != -1:
                break
            # 模拟点击下一页
            time.sleep(1)
            elem = driver.find_element_by_class_name('next')
            elem.click()
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            self.handle_page_info(soup)


    # 处理页面信息
    def handle_page_info(self, soup):
        """
            :param soup page
            该函数用于获取页面信息并将数据进行保存
            :return null
        """
        question_list = []
        question_items = soup.findAll('li', {'class': 'question-list-item'})
        for question in question_items:
            question_dict = dict()
            question_dict['qid'] = question['data-qid']
            question_dict['title'] = question.a.get_text()
            question_dict['url'] = question.a['href']
            num = question.findAll('div', {'class': 'answer-num'})[0].get_text()
            question_dict['num'] = num
            question_dict['tag'] = []
            for tag in question.findAll('a', {'class': 'tag-item'}):
                question_dict['tag'].append(tag)

            # 将数据保存到redis 表中
            # 可以考虑使用多线程
            self.save_url_to_redis(question_dict['qid'], question_dict['url'])
            # 获取问题的信息
            #question_list.append(ZhidaoObj(question_dict))

    # 保存数据到redis
    def save_url_to_redis(self, qid, url):
        """
        为了保证效率，URL长度过长
        设计两个表：baiDuZhiDao_URL 存放 ID,URL字典信息， baiDuZhiDao_ID 存放
        :param qid, url:
        :return:
        """
        from settings import REDIS_QID_TB, REDIS_URL_TB
        # 先获取表中数据, set 是高效的, 并且不会增加重复的值
        self.pipeline.sadd(REDIS_QID_TB, qid).sadd(REDIS_URL_TB, url).execute()
        # 将数据保存到 mongodb中
        #self.save_question_to_mongodb(qid, url)

    # 保存数据到mongodb
    def save_question_to_mongodb(self, qid, url):
        # 回答数目
        #num = question_dict['num'].strip()[0]
        self.db.question.insert({'qid': qid, 'url': url})

if __name__ == "__main__":
    crawler = BaiduZhidaoCrawler()
    crawler.get_home_page()