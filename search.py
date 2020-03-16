'''

[1] [2,7] [3] [5] [8]


'''

from IndexBuilder import processText
from nltk.stem import PorterStemmer
import threading
from IndexHasher import getgroup
from Assignment1.PartA import filename
import os
import pickle
from collections import Counter

ps = PorterStemmer()
#resp_dict = {}
ngrams_dict = [dict(), dict(), dict()]
ngrams_occur_freq = [set(), set(), set()]
resp_dict = {}
pos_top_15 = {}


def searchfunc(term, n):
#     resp = {}
    filename = 'onegrams/'
    if n == 3:
        filename = 'threegrams/'
    elif n == 2:
        filename = 'twograms/'
    
    filename += term[0]
    length = len(term)
    for p in range(4):
        if p + 1 >= length - 1:
            filename += '_' + str(getgroup(term[p + 1]) + 1)
        else:
            filename += '_' + '1'
    
    if(os.path.exists(filename)):
        with open(filename, 'rb') as handle:
            mydict = pickle.load(handle)
            if term in mydict:
                resp_dict[term] = mydict[term][:-1].strip('[]').split(', ')
                ngrams_dict[n-1][term] = mydict[term][:-1].strip('[]').split(', ')
                
    #resp_dict[term] = resp[term]
    return resp_dict                


def sortbyoccurence(resp_dict, n):
    resp_id = Counter([x.split('|', 1)[0] for x in resp_dict[term]])
    sorted_resp_id = sorted(resp_id, key = resp_id.get, reverse = True)
    if len(sorted_resp_id) >= 15:
        ngrams_occur_freq[n] = set(sorted_resp_id[:15])
    else:
        ngrams_occur_freq[n] = set(sorted_resp_id)
    
    return

def getpos(top_45): # merge this with searchfunc
    pass
    

if __name__ == '__main__':
    term = 'Master of Computer of Science'
    o_term = term
    
    # Processing 
    term = processText(term)
    
    stemmedTokens = [ps.stem(token) for token in term.split()]
    
    stemmed_term = "".join(stemmedTokens)
    
    three_grams, two_grams, one_grams = {}, {}, {}
    ngrams = [three_grams, two_grams, one_grams]
    
    position = 0
    for idx, token in enumerate(stemmedTokens):
        gramTokens = [None, None, None]
        gramTokens[0] = token
        if idx + 1 < len(stemmedTokens):
            gramTokens[1] = gramTokens[0] + ' ' + stemmedTokens[idx + 1]
        if idx + 2 < len(stemmedTokens):
            gramTokens[2] = gramTokens[1] + ' ' + stemmedTokens[idx + 2]
        
        for index, ngram in enumerate(ngrams):
            tok = gramTokens[index]
            if not tok: continue
            if tok not in ngram:
                ngram[tok] = []
            ngram[tok].append(position)
        position += 1
    print(one_grams)
    print(two_grams)
    print(three_grams)
    
    # 5, 6, 7
    # tokens = list(three_grams.keys()) + list(two_grams.keys()) + list(one_grams.keys())
    d = {}
    for i in range(len(three_grams.keys())):
        d[i % 5] = threading.Thread(target=searchfunc, args=three_grams.keys()[i], 3)
        d[i % 5].start()
    for i in range(len(two_grams.keys())):
        d[5 + (i % 6)] = threading.Thread(target=searchfunc, args=two_grams.keys()[i], 2)
        d[5 + (i % 6)].start()
    for i in range(len(one_grams.keys())):
        d[11 + (i % 7)] = threading.Thread(target=searchfunc, args=one_grams.keys()[i], 1)
        d[11 + (i % 7)].start()
    
    
    for i in range(18):
        if d.get(i, None):
            d[i].join()
    
    # set top 15 of each ngrams
    ng = {}
    for i in range(3):
        ng[i] = threading.Thread(target=sortbyoccurence, args = (ngrams_dict[i], i))
        ng[i].start()
    
    for i in range(3):
        if ng.get(i, None):
            ng[i].join()
    
    top_45 = set()
    for i in ngrams_occur_freq:
        top_45 |= i
    
    # get positions into pos_top_45
    # given a set of docids return positoions into a dict named pos_top_15
    p = {}
    for i in range(len(top_45)):
        p[i] = threading.Thread(target = getpos, args = (top_45))
        p[i].start
    for i in range(len(top_45)):
        if p.get(i, None):
            p[i].join()
    
    
    # matches found = 0
    
    # search for 3 grams
    
    # list of doc-Ids and postions
    
    # check for intersection of doc Ids
    # sort based on positions - 2 groups
    # sort based on number of occurences
    # see if matches == 5
    
    # (common_terms/total_terms * pos_score * (sum of tfidfs)) * n
    
