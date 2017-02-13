# -*- coding:UTF-8 -*-
__author__ = 'xwk'
import xml.etree.ElementTree as ET      # 不安全
import xml.dom.minidom as minidom
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Converter(object):
    '''
    实现Python对象与xml之间的相互转换
    '''
    root = None     # 根节点
    def __init__(self):
        pass
    @staticmethod
    def create_root(root_tag):
        '''
        创建根节点
        :param root_tag:
        :return:
        '''
        root = ET.Element(root_tag)
        return root

    # 保存评论信息
    @staticmethod
    def save_comments_xml(class_obj):
        '''
        根据传入的对象的实例，根据对象的属性生成节点
        :param class_obj: 对象的实例
        :param rootTag: 根节点名称
        :return:
        '''
        attrs = None    # 保存对象的属性集
        elelist = []    # 节点列表
        try:
            attrs = class_obj.__dict__.keys()   # 获取该对象的所有属性
            print attrs
        except:
            print '传入的对象非法，不能正确获取对象的属性'
        # 保存每个节点
        attrs = ['id', 'question', 'keywords', 'description', 'bestAnswer']
        for attr in attrs:
            attr_value = getattr(class_obj, attr)   # 属性值
            attrE = ET.Element(attr)
            attrE.text = attr_value
            # 加入节点列表
            elelist.append(attrE)
            print '<'+attr+'>',attrE.text,'</'+attr+'>'
        best_qra_list = getattr(class_obj, 'best_qra')
        best_ara_list = getattr(class_obj, 'best_ara')
        while True:
            if len(best_ara_list) > 0:
                attrE = ET.Element('ara')
                attrE.text = best_ara_list.pop(0)
                elelist.append(attrE)
                print '<ara>'+attrE.text+'</ara>'
            if len(best_qra_list) > 0:
                attrE = ET.Element('pra')
                attrE.text = best_qra_list.pop(0)
                elelist.append(attrE)
                print '<pra>'+attrE.text+'</pra>'
            if len(best_qra_list) <= 0 and len(best_ara_list) <= 0:
                break

        answers_list = getattr(class_obj, 'answer_list')
        for answer in answers_list:
            attrE = ET.Element('answer')
            attrE.text = answer[0]
            elelist.append(attrE)
            print '<answer>'+attrE.text+'</answer>'
            while True:
                if len(answer[1]) > 0:
                    attrE = ET.Element('ara')
                    attrE.text = answer[1].pop(0)
                    elelist.append(attrE)
                    print '<ara>'+attrE.text+'</ara>'
                if len(answer[2]) > 0:
                    attrE = ET.Element('pra')
                    attrE.text = answer[2].pop(0)
                    elelist.append(attrE)
                    print '<pra>',attrE.text,'</pra>'
                if len(answer[1]) <= 0 and len(answer[2]) <= 0:
                    break
        return elelist

    @staticmethod
    def class_to_xml(class_obj):
        '''
        Python自定义模型类转换成xml,转换成功返回的是xml根节点
        :param class_obj:
        :param rootTag:
        :return:
        '''
        try:
            class_name = class_obj.__class__.__name__      # 类名
            root = Converter.create_root(class_name)
            elelist = Converter.save_comments_xml(class_obj)
            for ele in elelist:
                root.append(ele)
            return root
        except:
            print '转换出错，请检查传入的对象是否正确'
            return None

    @staticmethod
    def get_xml_string(element, default_encoding='utf-8'):
        '''
        根据节点返回格式化的xml字符串
        :param element:
        :param default_encoding:
        :return:
        '''
        try:
            # rough_string = ET.tostring(element, encoding=default_encoding, method="xml")
            rough_string = ET.tostring(element, encoding=default_encoding, method="xml")
            reparsed = minidom.parseString(rough_string)
            results = reparsed.toprettyxml(indent=" ", encoding=default_encoding)

            xmlStr = results.replace('\t', '').replace('\n', '')
            xmlDomObject = minidom.parseString(xmlStr)
            xmlStr = xmlDomObject.toprettyxml(indent = '  ', encoding = 'utf-8')
            results = ''
            for temp in xmlStr.split('\n'):
                if (temp.strip(' ') == ''):
                    pass
                else:
                    results = results + temp
                    results += '\n'
            return results[:len(results)-1]
        except:
            print 'get_xml_string：传入的节点不能正确转换为xml，检查传入的节点数据是否正确'
            return ''

    @staticmethod
    def save_xml(comment):
        # 判断文件是否存在
        import os
        if os.path.isfile('../../xmlFile/comments.xml'):
            tree = ET.parse('../../xmlFile/comments.xml')
            temp_root = tree.getroot()
            root = Converter.class_to_xml(comment)
            temp_root.append(root)
        else:
            temp_root = Converter.create_root('Comment_list')
            root = Converter.class_to_xml(comment)
            temp_root.append(root)
        content = Converter.get_xml_string(temp_root)
        print content
        #with open('../xmlFile/comments.xml', 'ab') as f:
        """
        with open('../../xmlFile/comments.xml', 'wb') as f:
            f.write(content)
            pass
        """

class Person:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
if __name__ == '__main__':
    from crawler.app.zhidao_obj import Comment
    id = '2'
    question = '把自己拍到的视频传到网上让别人收看，能挣钱吗？_百度知道'
    keywords = '视频,挣钱'
    description = '把自己拍到的视频传到网上让别人收看，能挣钱吗？您好，很高兴回答您的问题。在中国，' \
                          '大多数网站是无法保护知识产权的，所以您如果要保护自己的视频所有权的话最好' \
                          '直接联系当地媒体来获得一定的信息费收入。希望我的'
    best_answer = '您高兴答您问题数网站保护知识产权所您要保护自视频所权直接联系媒体获定信息费收入希望我答能帮助您'
    qRA = ['我么1','wom2']
    aRA = ['您好，流2', 'test4']
    answers_list = [('test1',['he2', 'h4'], ['he2', 'h4']), ('test2',['he2', 'h4'], ['he2', 'h4'])]
    comment = Comment(id, question, keywords, description, best_answer, qRA, aRA, answers_list)
    Converter.save_xml(comment)