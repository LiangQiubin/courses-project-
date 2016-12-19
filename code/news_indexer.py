# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 16:48:03 2016

@author: Mr.Franck
"""

import os
import jieba
import lxml.etree as etree
import pymongo

import re

class Document(object):
    def __init__(self,id_doc,len_doc,tf):
        self.id_doc=id_doc
        self.len_doc=len_doc
        self.tf=tf
    def __str__(self):
        return(str(self.id_doc) + ',' + str(self.tf) + ',' + str(self.len_doc))

class Indexer(object):
    def __init__(self,stopwords_path,news_path):
        self.stopwords_path=stopwords_path
        self.news_path=news_path
        file_sw=open(stopwords_path).read().decode('utf-8')
        self.stopwords=set(file_sw.split('\n'))
        self.inverted_index={}
    def clean_news_cut(self,news_cut):
        dict_news={}
        len_news=0
        for word in news_cut:
            if word !='' and word not in self.stopwords:
                len_news+=1
                if word in dict_news:
                    dict_news[word]+=1
                else:
                    dict_news[word]=1
        return dict_news,len_news
        
    def save_index(self):
        client=pymongo.MongoClient("localhost", 27017)
        db = client["information_retrival_news"]
        collection=db['posting_list']
        for word, value in self.inverted_index.items():
            if value[0]<2:
                continue
            doc_str='\t'.join(map(str,value[1]))
            collection.insert({'word':word,'df':value[0],'doc':doc_str})
    def get_inverted_index(self):
        client=pymongo.MongoClient("localhost", 27017)
        db = client["information_retrival_news"]
        collection_news=db['news']
        files_name=os.listdir(self.news_path)
        news_id=0        
        len_avg=0 
        num_news=0
        for news_file in files_name: 
            text=open(self.news_path+'/'+news_file).read().decode('gbk','ignore')
            html = etree.HTML(text)
            urls=html.xpath(u"//url")
            contents=html.xpath(u"//content")
            titles=html.xpath(u'//contenttitle')
            for content,title,url in zip(contents,titles,urls):
                raw_news_title=title.text
                raw_news_content=content.text
                url=url.text
                if raw_news_content is None:
                    continue
                else:
                    news_content=re.sub(u'[^\u4e00-\u9fa5]','',raw_news_content)
                    if raw_news_title is None:
                        raw_news_title='无标题'
                        news_title=''
                    else:
                        news_title=re.sub(u'[^\u4e00-\u9fa5]','',raw_news_title)
                    news_cut=jieba.lcut_for_search(news_title+news_content)
                dict_news,len_news=self.clean_news_cut(news_cut)
                news_cut_str=','.join(dict_news.keys())
                collection_news.insert({'id':news_id,'title':raw_news_title,'news_content':raw_news_content,'url':url,'news_cut':news_cut_str}) 
                len_avg+=len_news
                for word,tf in dict_news.items():
                    doc=Document(news_id,len_news,tf)
                    if word in self.inverted_index:
                        self.inverted_index[word][0]+=1
                        self.inverted_index[word][1].append(doc)
                    else:
                        self.inverted_index[word]=[1,[doc]]
                num_news+=1
                news_id+=1 
            if num_news%1000==0:
                print num_news       
        len_avg=len_avg*1.0/num_news
        self.save_index()
        f=open('staic.txt','w')
        f.write('len_avg=%f\n'%len_avg)
        f.write('N=%d'%num_news)
        f.close()
def one_func(stopwords_path,news_path):
     my_index=Indexer(stopwords_path,news_path)
     my_index.get_inverted_index()

if __name__=='__main__':
    stopwords_path='D:/information_retrival/news_search/data/stopwords.txt'
    news_path='F:/data/news_reduced'
    my_index=Indexer(stopwords_path,news_path)
    my_index.get_inverted_index()
  
                        
                        
            
        
            
        
        
        
    
        