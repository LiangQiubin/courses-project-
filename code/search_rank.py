# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 22:05:05 2016

@author: Mr.Franck
"""
import jieba
import pymongo
import math
import time
import sim_hash
class SearchEngine(object):   
    def __init__(self,stopwords_path,hash_dict):       
        file_sw=open(stopwords_path).read()
        self.stopwords=set(file_sw.split('\n'))
        self.K1 = 1.5
        self.B = 0.75
        self.N = 298975
        self.len_avg=231.89
        self.hash_dict=hash_dict
    def clean_query_cut(self,query_cut):
        dict_query={}
        for word in query_cut:
            if word !='' and word not in self.stopwords:                
                if word in dict_query:
                    dict_query[word]+=1
                else:
                    dict_query[word]=1
        return dict_query
    def find_mongodb(self,word):
        client=pymongo.MongoClient("localhost", 27017)
        db = client["information_retrival_news"]
        collection=db['posting_list']
        related_doc=collection.find_one({'word':word})
        return related_doc
    def BM25(self,dict_query):
        BM25_scores={}
        for word in dict_query.keys():
            related_doc=self.find_mongodb(word)
            if related_doc is None:
                continue
            else:
                df=related_doc['df']
                docs=related_doc['doc'].split('\t')
                w=math.log((self.N - df + 0.5) / (df + 0.5),2)
                for doc in docs:
                    id_doc,tf,len_doc=doc.split(',')
                    id_doc=int(id_doc)
                    tf=int(tf)
                    len_doc=int(len_doc)
                    t_score=(self.K1 * tf * w)/ (tf + self.K1 * (1 - self.B + self.B * len_doc / self.len_avg))
                    if id_doc in BM25_scores:
                        BM25_scores[id_doc]+= t_score
                    else:
                        BM25_scores[id_doc]=t_score
                    
        BM25_scores=sorted(BM25_scores.items(),key=lambda item:item[1],reverse=1)
        
        if len(BM25_scores)==0:
            return 0,[]
        else:
            return 1,BM25_scores
            
    def search(self,query):
        query_cut=jieba.lcut_for_search(query)
        dict_query=self.clean_query_cut(query_cut)
        flag,result=self.BM25(dict_query)
        return flag, result[:50]
        
    def duplicated_detec(self,flag,result):
        docs=[i for i,score in result]
        present_docs={}
        duplicated_docs=[]
        length=min(50,len(result))
        for i in range(length):
            if docs[i] not in duplicated_docs:
                for j in range(i+1,length):                
                    distance=self.haiming_d(docs[i],docs[j])
                    if distance<3:
                        duplicated_docs.append(docs[j])
                        if docs[i] not in present_docs:
                            present_docs[docs[i]]=[docs[j]]
                        else:
                            present_docs[docs[i]].append(docs[j])
                if  docs[i] not in present_docs:
                    present_docs[docs[i]]=[]
        return present_docs
    def haiming_d(self,id_doc1,id_doc2):
        sh=sim_hash.SimHash()
        hash1=int(self.hash_dict[id_doc1])
        hash2=int(self.hash_dict[id_doc2])
        distance=sh.hamming_distance(hash1,hash2)
        return distance
        
            
        
if __name__=='__main__':
    
    query='黄岩岛'
    stopwords_path='D:/information_retrival/news_search/data/stopwords.txt'
    client=pymongo.MongoClient("localhost", 27017)
    db = client["information_retrival_news"]
    collection=db['hash']
    hash_dict={}
    for item in collection.find():
        id=item['id']
        hash_dict[id]=item['simhash']
    print 'done, reduced list'
    start=time.time()
    searcher=SearchEngine(stopwords_path,hash_dict)
    time_used=time.time()-start
    print time_used
    flag,result=searcher.search(query)
    docs=searcher.duplicated_detec(flag,result)
    
    
  
    

        
        