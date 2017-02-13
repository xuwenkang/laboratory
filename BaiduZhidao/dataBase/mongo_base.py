# -*- coding:utf-8 -*-
__author__ = 'xuwenkang'
import pymongo

# 获取mongodb 数据库实例
def get_mongodb_instance(db='test'):
    """
    :param db:数据库名称
    :return: 该数据库实例
    """
    from settings import MONGO_HOST, MONGO_PORT
    client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
    return client.baiduZhiDao


if __name__ == "__main__":
    db = get_mongodb_instance('baiduZhiDao')
    for temp in db.question.find():
        print temp['url']
