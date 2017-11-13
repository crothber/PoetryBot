# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 12:10:38 2017

@author: Carmi
"""

from languageModel import LanguageModel
from random import choice as choose
lm = LanguageModel()

corpus = open('cummings.txt', 'r').read().split('\n')[7:]
corpus = [l for l in corpus if l!='']
corpus = [l for l in corpus if not(len(l.split())==1 and l[0].isdigit())]
corpus = ''.join(corpus)
corpus = corpus.translate({ord(c): ' ' for c in '()?.-",;!'}).lower()
corpus = corpus.split()

lm.train([corpus])

twoPrev = choose(corpus)
prevWord = choose(lm.biDict[twoPrev])
poem = []
for i in range(100):
    tri_options = lm.triDict[(twoPrev, prevWord)]
    if len(tri_options)>1:
        thisWord = choose(tri_options)
    else:
        thisWord = choose(lm.biDict[prevWord])
    poem.append(thisWord)
    twoPrev = prevWord
    prevWord = thisWord
i = 0
lines = []
while i < len(poem):
    start = i
    end = i+choose([1,2,3,3,3,4,4,4,5,5,6,7])
    lines.append(poem[start:end+1])
    i = end
for line in lines:
    for word in line[:-1]:
        print(word, end=' ')
    print()
