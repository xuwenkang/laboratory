# -*- coding:utf-8 -*-
__author__ = 'xuwenkang'
import redis

# 获取redis 数据库实例
def get_db_instance(host, port, db=0):
    """
    :param host:
    :param port:
    :param db:
    :return: instance of redis client
    """
    r = redis.StrictRedis(host, port, db)
    return r

# 获取redis pipeline实例
def get_db_pipeline(host, port, db=0):
    """
    :param host:
    :param port:
    :param db:
    :return:
    """
    r = redis.StrictRedis(host, port, db)
    pipeline = r.pipeline()
    return pipeline

if __name__ == "__main__":
    import settings

    redis_inst = get_db_instance(settings.REDIS_HOST, settings.REDIS_PORT)
    redis_pipeline = get_db_pipeline(settings.REDIS_HOST, settings.REDIS_PORT)
    redis_pipeline.delete('foo')
    print redis_pipeline.get('foo').execute()
    #redis_inst.set('foo', '123')
    #redis_inst.delete('foo')
    #print redis_inst.get('foo')