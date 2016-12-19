# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 16:48:03 2016

@author: Mr.Franck
"""

#!congding = utf-8
__author__ = 'lcl'

from flask import Flask, render_template, request
import pymongo
import jieba
from search_rank import SearchEngine
app = Flask(__name__)

doc_dir_path = ''
db_path = ''
global page
global keys




@app.route('/')
def main():
    return render_template('search.html', error=True)


# 读取表单数据，获得doc_ID
@app.route('/search/', methods=['POST'])
def search():
    try:
        global keys
        global checked
        global present_docs
        global page
        checked = ['checked="true"', '', '']
        keys = request.form['key_word']
        flag,result=searcher.search(keys)        
        if flag:
            present_docs=searcher.duplicated_detec(flag,result)
            if len(present_docs)%10==0:
                page=range(1,len(present_docs)/10+1)
            else:
                page=range(1,len(present_docs)/10+2)
            docs=cut_page(0,1)
            return render_template('search.html', find=True,docs=docs,page=page)
        else:
            return render_template('search.html', find=False)
    except:
        print('search error')

@app.route('/search/page/<page_no>/', methods=['GET'])
def next_page(page_no):
    try:
        page_no = int(page_no)
        docs = cut_page(page_no-1, page_no)
        return render_template('search.html',docs=docs, page=page,
                               find=True)
    except:
        print('next error')

@app.route('/search/duplicate/<num_duplicated>/', methods=['GET'])
def show_duplicated_page(num_duplicated):
    client=pymongo.MongoClient("localhost", 27017)
    db = client["information_retrival_news"]
    collection=db['news']
    docs_set=[]
    try:
        num_duplicated=int(num_duplicated)
        id_docs_duplicated=present_docs[num_duplicated]
        for id_ in id_docs_duplicated:
            item=collection.find_one({'id':id_})
            doc={'id':item['id'],'title':item['title'],'snippet':item['news_content'][:140]+'...','url':item['url']}
            docs_set.append(doc)
        return render_template('duplicated.html',docs=docs_set)
    except:
        print ('duplicated error')
        


def cut_page(page_previous, page_current):
    client=pymongo.MongoClient("localhost", 27017)
    db = client["information_retrival_news"]
    collection=db['news']
    docs_set=[]
    for id_ in present_docs.keys()[page_previous*10:page_current*10]:      
        item=collection.find_one({'id':id_})
        num_duplicated=len(present_docs[id_])
        doc={'id':item['id'],'title':item['title'],'snippet':item['news_content'][:140]+'...','url':item['url'],'num_duplicated':num_duplicated}
        docs_set.append(doc)
    return docs_set

if __name__ == '__main__':
    jieba.initialize()
    stopwords_path='D:/information_retrival/news_search/data/stopwords.txt'
    client=pymongo.MongoClient("localhost", 27017)
    db = client["information_retrival_news"]
    collection=db['hash']
    hash_dict={}
    for item in collection.find():
        id=item['id']
        hash_dict[id]=item['simhash']
    searcher=SearchEngine(stopwords_path,hash_dict)
    app.run(debug=True)
















