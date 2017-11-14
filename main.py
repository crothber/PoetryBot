# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 12:10:38 2017

@author: Carmi
"""
# IMPORTS
from languageModel import LanguageModel, HMM
from random import choice as choose
from collections import defaultdict

# TRAIN LANGUAGE MODEL FROM CUMMINGS
print('training cummings language model...')
cummings = open('cummings.txt', 'r').read().split('\n')[7:]
cummings = [l for l in cummings if l!='']
cummings = [l for l in cummings if not(len(l.split())==1 and l[0].isdigit())]
cummings = ' |n| '.join(cummings)
cummings = cummings.translate({ord(c): ' ' for c in '()?.-",;!'}).lower()
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
    print('training from brown...')
    posLM.train(brown)
    print('tagging cummings...')
    cummings_lines = [l.split() for l in ' '.join(cummings).split('|n|')]
    cummings_tagged = []
    i = 0
    for line in cummings_lines:
        i += 1
        if i%400==0:
            print(str(int(100*i/2198)) + '% done', end='\t')
        cummings_tagged.extend(posLM.viterbi_tag(line))
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
    
    poem = """since feeling is first
    who pays any attention
    to the syntax of things
    will never wholly kiss you;
    wholly to be a fool
    while Spring is in the world
    my blood approves,
    and kisses are a better fate
    than wisdom
    lady i swear by all flowers. Don’t cry
    – the best gesture of my brain is less than
    your eyelids’ flutter which says
    we are for each other; then
    laugh, leaning back in my arms
    for life’s not a paragraph
    And death i think is no parenthesis"""
    
    poem = poem.translate({ord(c): '' for c in '()?.-",;!’'}).lower()
    lines = [line for line in poem.split('\n') if line!='']
    
    for line in lines:
        tagged_line = posLM.viterbi_tag(line.split())
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
