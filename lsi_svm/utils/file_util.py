# -*- coding:utf-8 -*-
import os
import codecs
import re
from sklearn.metrics import f1_score, recall_score, precision_score

class FileUtil():
    """
    文件操作类
    """
    @staticmethod
    def get_stopping_words_by_file(file_name):
        """
        字典查询速度快
        :param file_name:
        :return:
        """
        file_data = codecs.open(file_name, 'r', encoding='utf-8').read()
        stopping_words_dict = {}
        for line in file_data.strip().split('\n'):
            stopping_words_dict[line.strip()] = 1
        return stopping_words_dict

    @staticmethod
    def rm_char(text):
        text = re.sub('\u3000', '', text)
        text = re.sub(' ', '', text)
        return text

    @staticmethod
    def rm_tokens(words):
        stop_words_dict = FileUtil.get_stopping_words_by_file('../utils/stopwords_zh.txt')
        words = list(words)
        return [word for word in words if word not in stop_words_dict]

    @staticmethod
    def checked_pred(data_tag, data_pred):
        if data_tag.__len__() != data_pred.__len__():
            raise RuntimeError('The length of data tag and data pred should be the same')
        err_count = 0
        for i in range(data_tag.__len__()):
            if data_tag[i] != data_pred[i]:
                err_count += 1
        err_ratio = err_count / data_tag.__len__()
        print("\tPrecision: %1.3f" % precision_score(data_tag, data_pred))
        print("\tRecall: %1.3f" % recall_score(data_tag, data_pred))
        print("\tF1: %1.3f\n" % f1_score(data_tag, data_pred, average='weighted'))
        return [err_count, err_ratio]

    @staticmethod
    def load_folders(par_path):
        for file in os.listdir(par_path):
            file_abspath = os.path.join(par_path, file)
            if os.path.isdir(file_abspath): # if file is a folder
                yield file_abspath

    @staticmethod
    def read_file_by_dir(par_path):
        # 获取二级目录
        for dir_name in FileUtil.load_folders(par_path):
            try:
                catg = dir_name.split(os.sep)[-1]
                for f in os.listdir(dir_name):
                    f_read = codecs.open(dir_name + '//' + f, 'r', encoding='utf-8')
                    # 去掉尾部空格 和 换行
                    # file_list.append(f_read.read())
                    # 使用生成器，不必将所有数据读入到内存中
                    yield catg, f_read.read().strip()
            except:
                print('这不是一个目录')

if __name__ == '__main__':
    # note 文件夹名后面加 /
    #print(FileUtil.read_file_by_dir('E:\\xwk\\数据\\清华大学数据集\\THUCNews\\THUCNews\\财经/'))
    #FileUtil.get_stopping_words_by_file('../stopwords.txt')
    #print(FileUtil.get_stopping_words_by_file('stopwords_zh.txt'))
    #print(FileUtil.rm_token(['first', '你好']))
    print(FileUtil.rm_char('wo sh'))