# -*- coding:UTF-8 -*-
__author__ = 'xwk'
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Converter(object):
    def __init__(self):
        pass

    # 保存评论信息
    @staticmethod
    def save_comments_xml(class_obj):
        attrs = None    # 保存对象的属性集
        elelist = '<comment>'    # 节点列表
        try:
            attrs = class_obj.__dict__.keys()   # 获取该对象的所有属性
            print attrs
        except:
            print '传入的对象非法，不能正确获取对象的属性'
        # 保存每个节点
        attrs = ['id', 'question', 'keywords', 'description', 'bestAnswer']
        for attr in attrs:
            attr_value = getattr(class_obj, attr)   # 属性
            elelist += ('<'+attr+'>'+str(attr_value)+'</'+attr+'>')
            elelist += '\n'

        best_qra_list = getattr(class_obj, 'best_qra')
        best_ara_list = getattr(class_obj, 'best_ara')
        while True:
            if len(best_qra_list) > 0:
                text = best_qra_list.pop(0)
                elelist += ('<pra>'+text+'</pra>')
                elelist += '\n'
            if len(best_ara_list) > 0:
                text = best_ara_list.pop(0)
                elelist += ('<ara>'+text+'</ara>')
                elelist += '\n'
            if len(best_qra_list) <= 0 and len(best_ara_list) <= 0:
                break

        answers_list = getattr(class_obj, 'answer_list')
        for answer in answers_list:
            text = answer[0]
            elelist += ('<answer>'+text+'</answer>')
            elelist += '\n'
            while True:
                if len(answer[1]) > 0:
                    text = answer[1].pop(0)
                    elelist += ('<pra>'+text+'</pra>')
                    elelist += '\n'
                if len(answer[2]) > 0:
                    text = answer[2].pop(0)
                    elelist += ('<ara>'+text+'</ara>')
                    elelist += '\n'
                if len(answer[1]) <= 0 and len(answer[2]) <= 0:
                    break
        elelist += '</comment>'
        elelist += '\n'
        return elelist

    @staticmethod
    def save_xml(comment):
        # 判断文件是否存在
        content = Converter.save_comments_xml(comment)
        print content
        with open('../../xmlFile/comments.xml', 'ab') as f:
            f.write(content)
            pass