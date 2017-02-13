# -*- coding: utf-8 -*-
__author__ = 'xwk'
"""
    抓取代理ip并用多线程快速验证
"""
# 1、构造合理的 HTTP 请求头
import requests
import re
from bs4 import BeautifulSoup

session = requests.Session()
headers = {"User-Agent":"Mozilla/5.0(Macintosh; Intel Mac OS X 10_9_5)"
                        "AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
           "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
#西刺代理   或者使用 快代理
pre_url = "http://www.xicidaili.com/nn/"
#req = session.get(url, headers=headers)
#print req.
# text
def get_proxy():
    proxy_list = []
    #for page in range(1, 20):
    for page in range(1, 10):
        if page != 1:
            req = session.get(pre_url+str(page), headers=headers)
            #截取<td>与</td>之间第一个数为数字的内容
            pattern = re.compile('<td>(\d.*?)</td>')
            ip_page = re.findall(pattern, str(req.text.encode('utf-8')))
            # 第一个为ip，第二个为端口, 第三个和第四个没用
            i = 0
            while i < len(ip_page):
                ip = ip_page[i]
                port = ip_page[i+1]
                i += 4
                proxy_list.append("http://" + ip + ':' + port)
    return proxy_list

import threading
import socket
# 验证代理IP有效性的方法
# 创建一个锁
lock = threading.Lock()
proxy_list = []
def validate_proxy(proxy):
    headers = {"Content-type": "application/x-www-form-urlencoded",
           'Accept-Language':'zh-CN,zh;q=0.8',
           'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Connection": "close",
           "Cache-Control": "no-cache"}
    # 设置全局超时时间
    #socket.setdefaulttimeout(5)
    socket.setdefaulttimeout(2)
    # 爬取的URL
    url = "http://www.xicidaili.com/nn/1"
    try:
        s = requests.Session()
        proxy = {"http": proxy}
        s.get(url, headers=headers, proxies=proxy)
        # 获得锁
        lock.acquire()
        print(proxy, 'is ok')
        proxy_list.append(proxy)
        # 释放锁
        lock.release()
    except Exception as e:
        lock.acquire()
        print(proxy, e)
        lock.release()

# 多线程验证
def mul_validate():
    """
    threads = []
    proxy_list = get_proxy()
    for proxy in proxy_list:
        thread = threading.Thread(target=validate_proxy, args=[proxy])
        threads.append(thread)
        thread.start()
    # 阻塞主进程，等待所有子进程结束
    for thread in threads:
        thread.join()
    """
    import threadpool
    pool = threadpool.ThreadPool(50)
    requests = threadpool.makeRequests(validate_proxy, get_proxy())
    [pool.putRequest(req) for req in requests]
    pool.wait()

mul_validate()
print proxy_list