# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 12:10:38 2017

@author: Carmi
"""
# IMPORTS
from languageModel import LanguageModel
from hmm import HMM
from random import choice as choose
from collections import defaultdict
import csv

# TRAIN LANGUAGE MODEL FROM CUMMINGS
print('training cummings language model...')
cummings = open('cummings.txt', 'r').read().split('\n')[7:]
cummings = [l for l in cummings if l!='']
cummings = [l for l in cummings if not(len(l.split())==1 and l[0].isdigit())]
cummings = ' |n| '.join(cummings)
cummings = cummings.translate({ord(c): ' ' for c in '()?.-",;:!'}).lower()
cummings_lines = [line.split() for line in cummings.split('|n|')]
cummings = cummings.split()
lm = LanguageModel()
lm.train([cummings])
print('done!')

# TRAIN POS-TAGGER FROM BROWN
train_pos = input('prepare part-of-speech model, as well? (y/n) ')
if train_pos == 'y':
    print('preparing POS language model (this may take a while...)')
    brown = open('browntag_nolines.txt','r').read().split('\n')
    brown_split = []
    for line in brown:
        brown_split.append([])
        line = line.split()
        for word in line:
            brown_split[-1].append(tuple(word.split('_')))
    brown = [line for line in brown_split if line != []]
    posLM = HMM()
    print('\ttraining from brown...')
    posLM.train(brown)
    print('\ttagging cummings...')
    with open('cummings_tagged.csv', 'r') as f:
        reader = csv.reader(f)
        cummings_tagged = list(reader)
    posToWord = defaultdict(list)
    for pair in cummings_tagged:
        posToWord[pair[1]].append(pair[0])
    print('done!')

# N-GRAM GENERATE A POEM
def ngramGenerate():
    twoPrev = choose(cummings)
    prevWord = choose(lm.biDict[twoPrev])
    poem = []
    for i in range(65):
        tri_options = lm.triDict[(twoPrev, prevWord)]
        if len(tri_options)>1:
            thisWord = choose(tri_options)
        else:
            thisWord = choose(lm.biDict[prevWord])
        poem.append(thisWord)
        twoPrev = prevWord
        prevWord = thisWord
    print(' '.join(poem).replace('|n| ','\n'))

# POS-GENERATE A POEM
def posGenerate():
    
    lines = [choose(cummings_lines) for i in range(10)]
    
    for line in lines:
        tagged_line = posLM.viterbi_tag(line)
        for pair in tagged_line:
            wordOptions = posToWord[pair[1]]
            if len(wordOptions)>0:
                print(choose(wordOptions), end=" ")
        print()

another = 'y'
while another == 'y':
    poemType = input('what type of poem would you like to generate? (ngram or pos) ')
    if poemType == 'ngram':
        ngramGenerate()
    elif poemType == 'pos':
        posGenerate()
    else:
        print('oops! not sure what kind of poem that is.')
    another = input('generate another poem? (y/n) ')
