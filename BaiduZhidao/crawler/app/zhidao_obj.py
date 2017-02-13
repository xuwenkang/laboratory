# -*- coding:utf-8 -*-
__author__ = 'xuwenkang'
"""
    百度知道评论
"""
class Comment:
    def __init__(self, id, question, keywords, description, best_answer, qRA, aRA, answers_list):
        self.id = id
        self.question = question
        self.keywords = keywords
        self.description = description
        self.bestAnswer = best_answer
        self.best_qra = qRA
        self.best_ara = aRA
        self.answer_list = answers_list
