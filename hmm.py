# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 20:37:32 2017

@author: Carmi
"""

from collections import defaultdict

class HMM:

    def __init__(self):
        
        # Start, stop, unknown tokens
        self.START = '<S>'
        self.STOP = '</S>'
        self.UNK = '*UNKNOWN*'
        
        # Counters
        self.posCounter = defaultdict(float)
        self.wordPOScounter = defaultdict(float)
        self.biCounter = defaultdict(float)
        
        # Smoothing constants
        self.alpha = .1
        self.beta = .01
        
        # Vocab (observables) and pos_set (states)
        self.vocab = set()
        self.pos_set = set()
        
        # Dictionaries for faster probability lookup
        self.prob_bigram = defaultdict(dict)
        self.prob_word_given_pos = defaultdict(dict)
        
    def train(self, trainingSentences):
        
        for sentence in trainingSentences:
            
            # First word of each sentence
            self.vocab.add(sentence[0][0])
            self.pos_set.add(sentence[0][1])
            
            self.posCounter[sentence[0][1]] += 1
            self.wordPOScounter[sentence[0]] += 1
            
            self.posCounter[self.START] += 1
            self.wordPOScounter[(self.START, self.START)] += 1
            self.biCounter[(self.START, sentence[0][1])] += 1
            
            # Middle words in each sentence
            lenSent = len(sentence)
            for i in range(1, lenSent):
                self.vocab.add(sentence[i][0])
                self.pos_set.add(sentence[i][1])
                
                self.posCounter[sentence[i][1]] += 1
                self.wordPOScounter[sentence[i]] += 1
                self.biCounter[(sentence[i-1][1],sentence[i][1])] += 1
            
            # Final word of each sentence
            self.posCounter[self.STOP] += 1
            self.wordPOScounter[(self.STOP, self.STOP)] += 1
            self.biCounter[(sentence[-1][1], self.STOP)] += 1
        
        # Cache all probabilities seen in training data
        for sent in trainingSentences:
            if sent[0][1] not in self.prob_word_given_pos[sent[0][0]]:
                self.prob_word_given_pos[sent[0][0]][sent[0][1]] = self.getWordProbability(sent[0][0], sent[0][1])
            if sent[0][1] not in self.prob_bigram[self.START]:
                self.prob_bigram[self.START][sent[0][1]] = self.get_POS_probability(self.START, sent[0][1])
            for i in range(1, len(sent)):
                if sent[i][1] not in self.prob_word_given_pos[sent[i][0]]:
                    self.prob_word_given_pos[sent[i][0]][sent[i][1]] = self.getWordProbability(sent[i][0], sent[i][1])
                if sent[i][1] not in self.prob_bigram[sent[i-1][1]]:
                    self.prob_bigram[sent[i-1][1]][sent[i][1]] = self.get_POS_probability(sent[i-1][1], sent[i][1])
            if self.STOP not in self.prob_bigram[sent[-1][1]]:
                self.prob_bigram[sent[-1][1]][self.STOP] = self.get_POS_probability(sent[-1][1], self.STOP)
        # NOTE: prob_bigram now allows for the lookup of previously seen word-tag pairs -- that is, given
        # a word, we can use its value in the prob_bigram dictionary to determine what tags it has been assigned
        # in the training data.
            
        # Vocab is all words seen so far, plus STOP and UNK
        self.vocab.add(self.UNK)
        self.vocab.add(self.STOP)
        # POS_set is all parts of speech in the training data
        self.pos_set.add(self.START)
        self.pos_set.add(self.STOP)
        
        # Total number of POS bigrams
        self.total = len(self.biCounter.keys())
    
    # Get the probability of a word given a POS
    def getWordProbability(self, word, pos):
        
        if pos in self.prob_word_given_pos[word]:
            return self.prob_word_given_pos[word][pos]

        c_pos_word = self.wordPOScounter[(word, pos)]
        c_pos = self.posCounter[pos]
        V = len(self.vocab)
        
        probability = (c_pos_word + self.alpha) / (c_pos + (V*self.alpha))
        
        self.prob_word_given_pos[word][pos] = probability
        
        return probability
    
    # Get the probability of a POS given a previous POS
    def get_POS_probability(self, prevPOS, nextPOS):
        
        if nextPOS in self.prob_bigram[prevPOS]:
            return self.prob_bigram[prevPOS][nextPOS]
        c_p1p2 = self.biCounter[(prevPOS, nextPOS)]
        c_p1 = self.posCounter[prevPOS]
        V = len(self.vocab)
        
        probability = (c_p1p2 + self.beta) / (c_p1 + (V *self.beta))
        
        self.prob_bigram[prevPOS][nextPOS] = probability
        
        return probability
    
    # Use the Viterbi algorithm. In order to speed up tagging time, words that appear in the training
    # data may only be assigned tags we have already seen them with. To change this, simply remove the
    # calculations of 'potential tags' and replace with pos_set. This will result in each sentence having
    # a complexity of (len(pos_set)*len(sent))+1. Since there are over 800 tags in the training data, this
    # is a significant reduction in speed.
    def viterbi_tag(self, sent):
        
        viterbi = {}
        backpointer = {}
        
        # Determine probabilities of each tag for the first word
        potentialTags = self.prob_word_given_pos[sent[0]]
        if potentialTags == {}:
            potentialTags = self.pos_set
        for tag in potentialTags:
            viterbi[(tag, 0)] = self.get_POS_probability(self.START, tag) * self.getWordProbability(sent[0], tag)
            backpointer[(tag, 0)] = 0
        
        # For each subsequent word, determine the maximum probability of each tag and use that to
        # point back to the most likely previous tag
        for t in range(1, len(sent)):
            potentialTags = self.prob_word_given_pos[sent[t]]
            if potentialTags == {}:
                potentialTags = self.pos_set
            for tag in potentialTags:
                potentialPrevTags = self.prob_word_given_pos[sent[t-1]]
                if potentialPrevTags == {}:
                    potentialPrevTags = self.pos_set
                viterbi[(tag, t)] = max([(viterbi[prevTag, t-1] * self.get_POS_probability(prevTag, tag) * self.getWordProbability(sent[t], tag)) for prevTag in potentialPrevTags])
                backpointer[(tag, t)] = max(potentialPrevTags, key=lambda prevTag: (viterbi[prevTag, t-1] * self.get_POS_probability(prevTag, tag)))
        
        # Compute most likely final tag given previous probability calculations for previous tags
        potentialPrevTags = self.prob_word_given_pos[sent[-1]]
        if potentialPrevTags == {}:
            potentialPrevTags = self.pos_set
        viterbi[(self.STOP, len(sent))] = max([(viterbi[prevTag, len(sent)-1] * self.get_POS_probability(prevTag, self.STOP)) for prevTag in potentialPrevTags])
        backpointer[(self.STOP, len(sent))] = max(potentialPrevTags, key=lambda prevTag: (viterbi[prevTag, len(sent)-1] * self.get_POS_probability(prevTag, self.STOP)))
        
        # Follow back pointers from STOP, reversing in the process.
        tag = self.STOP
        tagged_sent = []
        for i in range(len(sent)):
            j = len(sent)-i
            tag = backpointer[tag, j]
            tagged_sent.insert(0, (sent[j-1], tag))
        return tagged_sent