# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 10:38:50 2017

@author: Carmi
"""
from collections import defaultdict

class LanguageModel ():
    def __init__(self):
        self.START = '<S>'
        self.STOP = '</S>'

        self.totalWords = 0
        self.uniCounter = defaultdict(float)
        self.biCounter = defaultdict(float)
        self.triCounter = defaultdict(float)
        
        self.biDict = defaultdict(list)
        self.triDict = defaultdict(list)
        
        self.probCounter = defaultdict(float)
    
    def train(self, trainingSentences):
        for sentence in trainingSentences:
            
            self.totalWords += len(sentence)
            
            sent = [self.START, self.START]
            sent.extend(sentence)
            sent.extend([self.STOP, self.STOP])
            
            for i in range(2, len(sent)-2):
                self.uniCounter[sent[i]] += 1
                self.biCounter[(sent[i-1],sent[i])] += 1
                self.biDict[sent[i-1]].append(sent[i])
                self.triCounter[(sent[i-2],sent[i-1],sent[i])] += 1
                self.triDict[(sent[i-2],sent[i-1])].append(sent[i])
            
        self.totalWords = sum(self.uniCounter.values())
        self.uniCounter[self.START] = len(trainingSentences)
        self.biCounter[(self.START, self.START)] = len(trainingSentences)
        self.triCounter[(self.START, self.START, self.START)] = len(trainingSentences)
           
    def prob(self, w1, w2=None, w3=None):
        if w3 != None:
            if (w1, w2, w3) not in self.probCounter.keys():
                c_w1w2w3 = self.triCounter[(w1, w2, w3)]
                c_w1w2 = self.biCounter[(w1, w2)]
                if c_w1w2 == 0:
                    probability = 0
                else:
                    probability = c_w1w2w3 / c_w1w2
                self.probCounter[(w1, w2, w3)] = probability
            return self.probCounter[(w1, w2, w3)]
        if w2 != None:
            if (w1, w2) not in self.probCounter.keys():
                c_w1w2 = self.biCounter[(w1, w2)]
                c_w1 = self.uniCounter[w1]
                if c_w1 == 0:
                    probability = 0
                else:
                    probability = c_w1w2 / c_w1
                self.probCounter[(w1, w2)] = probability
            return self.probCounter[(w1, w2)]
        else:
            if w1 not in self.probCounter.keys():
                self.probCounter[w1] = self.uniCounter[w1]/self.totalWords
            return self.probCounter[w1]