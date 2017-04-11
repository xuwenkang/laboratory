# coding:utf-8
from gensim import corpora, models
from scipy.sparse import csr_matrix
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn import svm
import numpy as np
import os, re, time, logging
import jieba
import pickle as pkl

from utils.file_util import FileUtil

logging.basicConfig(level=logging.WARNING,
                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                     datefmt='%a, %d %b %Y %H:%M:%S',
                     )
def convert_doc_to_wordlist(str_doc, cut_all):
    """
    将文件内容转换成词典
    """
    sent_list = str_doc.split('\n')
    # 移除一些字符， 如\u3000 空格
    sent_list = map(FileUtil.rm_char, sent_list)
    # 分词，并且去掉停用词
    word_2dlist = [FileUtil.rm_tokens(jieba.cut(part, cut_all=cut_all)) for part in sent_list]
    word_list = sum(word_2dlist, [])
    return word_list

def svm_classify(train_set, train_tag, test_set, test_tag):
    """
    首先实现一个 linear kernel 的分类器
    """
    clf = svm.LinearSVC()
    clf_res = clf.fit(train_set, train_tag)
    train_pred = clf_res.predict(train_set)
    test_pred = clf_res.predict(test_set)

    train_err_num, train_err_ratio = FileUtil.checked_pred(train_tag, train_pred)
    test_err_num, test_err_ratio = FileUtil.checked_pred(test_tag, test_pred)

    print('=== 分类训练完毕，分类结果如下 ===')
    print('训练集误差: {e}'.format(e=train_err_ratio))
    print('检验集误差: {e}'.format(e=test_err_ratio))
    return clf_res

if __name__ == '__main__':
    data_path = 'E:\\xwk\\数据\\清华大学数据集\\THUCNews\\THUCNews\\'
    tmp_data_path = 'E:\\xwk\\数据\\清华大学数据集\\THUCNews\\tmp\\'
    path_dictionary = os.path.join(tmp_data_path, 'THUNews.dict')
    path_tmp_tfidf = os.path.join(tmp_data_path, 'tfidf_corpus')
    path_tmp_lsi = os.path.join(tmp_data_path, 'lsi_corpus')
    path_tmp_lsimodel = os.path.join(tmp_data_path, 'lsi_model.pkl')
    path_tmp_predictor = os.path.join(tmp_data_path, 'predictor.pkl')

    dictionary = None
    corpus_tfidf = None
    corpus_lsi = None
    lsi_model = None
    predictor = None
    if not os.path.exists(tmp_data_path):
        os.makedirs(tmp_data_path)

    # n 表示抽样率，n 抽 1
    n = 10

    # # ===================================================================
    # # # # 第一阶段，  遍历文档，生成词典,并去掉频率较少的项
    #       如果指定的位置没有词典，则重新生成一个。如果有，则跳过该阶段
    t0 = time.time()
    if not os.path.exists(path_dictionary):
        print('=== 未检测到有词典存在，开始遍历生成词典 ===')
        dictionary = corpora.Dictionary()
        files = FileUtil.read_file_by_dir(data_path)

        for i, content in enumerate(files):
            if i % n == 0:
                catg = content[0]
                file = content[1]
                file = convert_doc_to_wordlist(file, False)
                dictionary.add_documents([file])
                if int(i / n) % 1000 == 0:
                    print('{t} *** {i} \t docs has been dealed'
                          .format(i=i, t=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        # 去掉词典中出现次数过少的
        small_freq_ids = [tokenid for tokenid, docfreq in dictionary.dfs.items() if docfreq < 5]
        dictionary.filter_tokens(small_freq_ids)
        dictionary.compactify()
        dictionary.save(path_dictionary)
        print('=== 词典已经生成 ===')
    else:
        print('=== 检测到词典已经存在，跳过该阶段 ===')
    print("第一阶段花费的时间为：{0}".format(time.time() - t0))

    t0 = time.time()
    # # ===================================================================
    # # # # 第二阶段，  开始将文档转化成tfidf
    if not os.path.exists(path_tmp_tfidf):
        print('=== 未检测到有tfidf文件夹存在，开始生成tfidf向量 ===')
        # 如果指定的位置没有tfidf文档，则生成一个。如果有，则跳过该阶段
        if not dictionary:
            dictionary = corpora.Dictionary.load(path_dictionary)
        os.makedirs(path_tmp_tfidf)
        files = FileUtil.read_file_by_dir(data_path)
        tfidf_model = models.TfidfModel(dictionary=dictionary)
        corpus_tfidf = {}
        for i, msg in enumerate(files):
            if i % n == 0:
                catg = msg[0]
                file = msg[1]
                word_list = convert_doc_to_wordlist(file, cut_all=False)
                # 生成
                file_bow = dictionary.doc2bow(word_list)
                file_tfidf = tfidf_model[file_bow]
                tmp = corpus_tfidf.get(catg, [])
                tmp.append(file_tfidf)
                if tmp.__len__() == 1:
                    corpus_tfidf[catg] = tmp

            if i % 10000 == 0:
                print('{i} files is dealed'.format(i=i))
        # 将 tfidf 中间结果存储起来
        catgs = list(corpus_tfidf.keys())
        for catg in catgs:
            corpora.MmCorpus.serialize('{f}{s}{c}.mm'.format(f=path_tmp_tfidf, s=os.sep, c=catg),
                                       corpus_tfidf.get(catg),
                                       id2word=dictionary)
            print('catg {c} has been transformed into tfidf vector'.format(c=catg))
        print('=== tfidf向量已经生成 ===')
    else:
        print('=== 检测到tfidf向量已经生成，跳过该阶段 ===')
    print("第二阶段花费的时间为：{0}".format(time.time() - t0))

    t0 = time.time()
    # # ===================================================================
    # # # # 第三阶段，  开始将tfidf转化成lsi
    if not os.path.exists(path_tmp_lsi):
        print('=== 未检测到有lsi文件夹存在，开始生成lsi向量 ===')
        if not dictionary:
            dictionary = corpora.Dictionary.load(path_dictionary)
        # 如果跳过了第二阶段，则从指定位置读取tfidf文档
        if not corpus_tfidf:
            print('--- 未检测到tfidf文档，开始从磁盘中读取 ---')
            # 从对应文件夹中读取所有类别
            files = os.listdir(path_tmp_tfidf)
            catg_list = []
            for file in files:
                t = file.split('.')[0]
                if t not in catg_list:
                    catg_list.append(t)

            # 从磁盘中读取 corpus
            corpus_tfidf = {}
            for catg in catg_list:
                path = '{f}{s}{c}.mm'.format(f=path_tmp_tfidf, s=os.sep, c=catg)
                corpus = corpora.MmCorpus(path)
                corpus_tfidf[catg] = corpus
            print('--- tfidf文档读取完毕，开始转化成lsi向量 ---')

        # 生成 lsi model
        os.makedirs(path_tmp_lsi)
        corpus_tfidf_total = []
        catgs = list(corpus_tfidf.keys())
        for catg in catgs:
            tmp = corpus_tfidf.get(catg)
            corpus_tfidf_total += tmp
        lsi_model = models.LsiModel(corpus=corpus_tfidf_total, id2word=dictionary, num_topics=50)
        # 将 lsi 模型存储到磁盘上
        lsi_file = open(path_tmp_lsimodel, 'wb')
        # 使用 pickle 进行压缩
        pkl.dump(lsi_model, lsi_file)
        lsi_file.close()
        # lsi model 已经生成，释放变量空间
        del corpus_tfidf_total
        # 生成corpus of lsi, 并逐步去掉 corpus of tfidf
        corpus_lsi = {}
        for catg in catgs:
            corpu = [lsi_model[doc] for doc in corpus_tfidf.get(catg)]
            corpus_lsi[catg] = corpu
            corpus_tfidf.pop(catg)
            corpora.MmCorpus.serialize('{f}{s}{c}.mm'.format(f=path_tmp_lsi, s=os.sep, c=catg),
                                       corpu,
                                       id2word=dictionary)
            print('=== {0}-lsi向量已经生成 ==='.format(catg))
        else:
            print('=== 检测到lsi向量已经生成，跳过该阶段 ===')
    print("第三阶段花费的时间为：{0}".format(time.time() - t0))


    t0 = time.time()
    # # ===================================================================
    # # # # 第四阶段，  分类
    if not os.path.exists(path_tmp_predictor):
        print('=== 未检测到判断器存在，开始进行分类过程 ===')
        # 如果跳过了第三阶段
        if not corpus_lsi:
            print('--- 未检测到lsi文档，开始从磁盘中读取 ---')
            files = os.listdir(path_tmp_lsi)
            catg_list = []
            for file in files:
                t = file.split('.')[0]
                if t not in catg_list:
                    catg_list.append(t)
            # 从磁盘中读取corpus
            corpus_lsi = {}
            for catg in catg_list:
                path = '{f}{s}{c}.mm'.format(f=path_tmp_lsi, s=os.sep, c=catg)
                corpus = corpora.MmCorpus(path)
                corpus_lsi[catg] = corpus
            print('--- lsi文档读取完毕，开始进行分类 ---')

        tag_list = []
        doc_num_list = []
        corpus_lsi_total = []
        catg_list = []
        files = os.listdir(path_tmp_lsi)
        for file in files:
            t = file.split('.')[0]
            if t not in catg_list:
                catg_list.append(t)
        for count, catg in enumerate(catg_list):
            tmp = corpus_lsi[catg]
            tag_list += [count] * tmp.__len__()
            doc_num_list.append(tmp.__len__())
            corpus_lsi_total += tmp
            corpus_lsi.pop(catg)

        # 将 gensim 中的 mm 表示转化成 numpy 矩阵表示
        data = []
        rows = []
        cols = []
        line_count = 0
        for line in corpus_lsi_total:
            for elem in line:
                rows.append(line_count)
                # 这是什么
                cols.append(elem[0])
                data.append(elem[1])
            line_count += 1
        # 稀疏矩阵 转成 密集矩阵， 不懂请百度
        lsi_matrix = csr_matrix((data, (rows, cols))).toarray()
        # 生成训练集和测试集
        rarray = np.random.random(size=line_count)
        train_set = []
        train_tag = []
        test_set = []
        test_tag = []
        for i in range(line_count):
            if rarray[i] < 0.8:
                train_set.append(lsi_matrix[i, :])
                train_tag.append(tag_list[i])
            else:
                test_set.append(lsi_matrix[i, :])
                test_tag.append(tag_list[i])

        # 生成分类器
        predictor = svm_classify(train_set, train_tag, test_set, test_tag)
        x = open(path_tmp_predictor, 'wb')
        pkl.dump(predictor, x)
        x.close()
    else:
        print('=== 检测到分类器已经生成，跳过该阶段 ===')
    print("第四阶段花费的时间为：{0}".format(time.time() - t0))

    t0 = time.time()
    # # ===================================================================
    # # # # 第五阶段，  对新文本进行判断
    if not dictionary:
        dictionary = corpora.Dictionary.load(path_dictionary)
    if not lsi_model:
        lsi_file = open(path_tmp_lsimodel, 'rb')
        lsi_model = pkl.load(lsi_file)
        lsi_file.close()
    if not predictor:
        x = open(path_tmp_predictor, 'rb')
        predictor = pkl.load(x)
        x.close()
    files = os.listdir(path_tmp_lsi)
    catg_list = []
    for file in files:
        t = file.split('.')[0]
        if t not in catg_list:
            catg_list.append(t)

    # 测试内容
    #demo_doc = """
     #   这次大选让两党的精英都摸不着头脑。以媒体专家的传统观点来看，要选总统首先要避免失言，避免说出一些“offensive”的话。希拉里，罗姆尼，都是按这个方法操作的。罗姆尼上次的47%言论是在一个私人场合被偷录下来的，不是他有意公开发表的。今年希拉里更是从来没有召开过新闻发布会。
      #  川普这种肆无忌惮的发言方式，在传统观点看来等于自杀。
       # """
    demo_doc = "货币战争中，量子基金的索罗斯击溃亚洲多国经济"
    print('原文本内容为：')
    print(demo_doc)
    demo_doc = list(jieba.cut(demo_doc, cut_all=False))
    # 转成字典
    demo_bow = dictionary.doc2bow(demo_doc)
    tfidf_model = models.TfidfModel(dictionary=dictionary)
    demo_tfidf = tfidf_model[demo_bow]
    demo_lsi = lsi_model[demo_tfidf]
    data = []
    cols = []
    rows = []
    for item in demo_lsi:
        data.append(item[1])
        cols.append(item[0])
        rows.append(0)
    demo_matrix = csr_matrix((data, (rows, cols))).toarray()
    x = predictor.predict(demo_matrix)
    print('分类结果为：{x}'.format(x=catg_list[x[0]]))
    print("第五阶段花费的时间为：{0}".format(time.time() - t0))