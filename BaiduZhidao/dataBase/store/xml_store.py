# -*- coding: UTF-8 -*-
__author__ = 'xuwenkang'

from xml.dom.minidom import parse, getDOMImplementation
import xml.dom.minidom

# 使用 minidom 解析器打开 XML文档
class XmlObj:
    def __init__(self):
        #DOMTree = xml.dom.minidom.parse('zhidao.xml')
        #self.collection = DOMTree.documentElement
        pass

    def write_to_xml(self):
        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "zhidao", None)
        top_element = newdoc.documentElement
        text = newdoc.createTextNode('Some textual content.')
        text.toxml()
        top_element.appendChild(text)
        import codecs
        f = file('test.xml', 'w')
        writer = codecs.lookup('utf-8')[3](f)
        newdoc.writexml(writer, )



XmlObj().write_to_xml()