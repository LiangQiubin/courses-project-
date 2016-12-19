# -*- coding: utf-8 -*-
"""
Created on Sun Dec 18 11:16:51 2016

@author: Mr.Franck
"""
from hashlib import md5
import pymongo
import math

class SimHash(object):
    def __init__(self, hashbits=128):
        self.N=298975        
        self.hashbits = hashbits
    def __str__(self):
        return str(self.hash)
  
    def simhash(self, features):
        v = [0] * self.hashbits
        for feature,weight in features.items(): 
            md5_hash=int(md5(feature.encode('gbk')).hexdigest(), 16)
            for i in range(self.hashbits):
                bitmask = 1 << i
                if md5_hash & bitmask :
                    v[i] += weight #查看当前bit位是否为1,是的话将该位+1
                else:
                    v[i] -= weight #否则的话,该位-1
        fingerprint = 0
        for i in range(self.hashbits):
            if v[i] >= 0:
                fingerprint += 1 << i
        return fingerprint #整个文档的fingerprint为最终各个位>=0的和
    
    #求海明距离
    def hamming_distance(self,hash1, hash2):
        x = (hash1 ^ hash2) & ((1 << self.hashbits) - 1)
        tot = 0;
        while x :
            tot += 1
            x &= x - 1
        return tot
    
    def MD5_hash(self, source):   
        if source == "":
            return 0
        else:
            h = int(md5(source).hexdigest(), 16)        
            return h
    def get_features(self,item,list_reduced):
        news_cut=item['news_cut'].split(',')
        features={}
        for word in news_cut:
            if word not in features and word in list_reduced:                
                df=list_reduced[word]
                tf=news_cut.count(word)
                len_doc=len(news_cut)
                tf_idf=(tf*1.0/len_doc)*math.log((self.N-df+0.5)/(df+0.5),2)
                features[word]=tf_idf
                break
        return features
    def cal_docs_hash(self,list_reduced):
        client=pymongo.MongoClient("localhost", 27017)
        db = client["information_retrival_news"]
        collection=db['news']
        hash_collection=db['hash1']
        news_id=0
        for item in collection.find():
            features=self.get_features(item,list_reduced)
            hash_value=self.simhash(features)
            hash_collection.insert({'id':news_id,'simhash':str(hash_value)})
            if news_id%100==0:
                print news_id
            news_id=news_id+1
    def get_dflist(self):
        print 'generate reduced list...'
        client=pymongo.MongoClient("localhost", 27017)
        db = client["information_retrival_news"]
        collection=db['posting_list']
        list_reduced={}
        for item in collection.find():
            word=item['word']
            list_reduced[word]=item['df']
        print 'done, reduced list'
        return list_reduced
if __name__=='__main__':
    sh=SimHash()
    list_reduced=sh.get_dflist()
    sh.cal_docs_hash(list_reduced)
        
        
    
    
    
    
    
    
    
    
    
    