# -*- coding:utf-8 -*-
__author__ = 'xwk'
"""
    multi thread
"""
import threadpool
from threading import Thread
from Queue import Queue

from questions import Question
# 创建消息队列
global url_queue
url_queue = Queue()

# 创建任务进程
def create_job(url):
    print url
    Question.get_question(url)

# url_list处理函数
def handle_url_list(url_list):
    pass


if __name__ == '__main__':
    import time
    start = time.time()
    # 获取url参数列表
    url_list = Question.mul_get_url()
    #print url_list
    # 创建线程池
    #pool = threadpool.ThreadPool(10)
    pool = threadpool.ThreadPool(5)
    requests = threadpool.makeRequests(create_job, url_list)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    end = time.time()
    print end-start