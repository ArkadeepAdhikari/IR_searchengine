'''

[1] [2,7] [3] [5] [8]


'''

from IndexBuilder import processText
from nltk.stem import PorterStemmer
import threading
from IndexHasher import getgroup
#from Assignment1.PartA import filename
import os
import pickle
from collections import Counter

ps = PorterStemmer()

ngrams_dict = [dict(), dict(), dict()]
ngrams_occur_freq = [list(), list(), list()]
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
        if p + 1 <= length - 1:
            filename += '_' + str(getgroup(term[p + 1]) + 1)
        else:
            filename += '_' + '1'
    filename += '.pickle'
    if(os.path.exists(filename)):
        with open(filename , 'rb') as handle:
            mydict = pickle.load(handle)
            if term in mydict:
                resp_dict[term] = mydict[term][:-1].strip('[]').split(', ')
                ngrams_dict[n-1][term] = mydict[term][:-1].strip('[]').split(', ')
                
    return resp_dict


def sortbyoccurence(ng_dict, n):
    val_list = []
    for k in ng_dict:
        val_list += ng_dict[k]
    resp_id = Counter([x.split('|', 1)[0] for x in val_list])
    ngrams_occur_freq[n] = resp_id.most_common((15)) # stores a tuple of (docId, count) for corresponding n_gram
    
    return

def getpos(doc_id):
    pass
    

if __name__ == '__main__':
    term = 'Master of Computer of Science'
    o_term = term
    
    # Processing 
    term = processText(term)
    
    stemmedTokens = [ps.stem(token) for token in term.split()]
    
    stemmed_term = "".join(stemmedTokens)
    
    three_grams, two_grams, one_grams = {}, {}, {}
    ngrams = [one_grams, two_grams, three_grams]
    
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
    #print(one_grams)
    #print(two_grams)
    #print(three_grams)
    #print(searchfunc('master of comput', 3))


    # 5 threads for onegrams, 6 for twograms, 7 for threegrams
    d = {}
    for i in range(len(three_grams.keys())):
        d[i % 5] = threading.Thread(target=searchfunc, args= (list(three_grams.keys())[i], 3))
        d[i % 5].start()
    for i in range(len(two_grams.keys())):
        d[5 + (i % 6)] = threading.Thread(target=searchfunc, args= (list(two_grams.keys())[i], 2))
        d[5 + (i % 6)].start()
    for i in range(len(one_grams.keys())):
        d[11 + (i % 7)] = threading.Thread(target=searchfunc, args= (list(one_grams.keys())[i], 1))
        d[11 + (i % 7)].start()
    for i in range(18):
        if d.get(i, None):
            d[i].join()

    #print(list(resp_dict.keys()))
    #print(ngrams_dict[2].keys())

    # set top 15 of each ngrams

    #print(sortbyoccurence(ngrams_dict[2], 2))


    ng = {}
    for i in range(3):
        ng[i] = threading.Thread(target=sortbyoccurence, args=(ngrams_dict[i], i))
        ng[i].start()

    for i in range(3):
        if ng.get(i, None):
            ng[i].join()
    print(ngrams_occur_freq)

'''
    top_45 = set()
    for i in ngrams_occur_freq:
        top_45 |= set(i)

    print(top_45)
    top_45 = list(top_45)

    # get positions into pos_top_45
    # given a set of docids return positions into a dict named pos_top_15
    p = {}
    for i in range(len(top_45)):
        p[i] = threading.Thread(target=getpos, args=(top_45[i][0]))
        p[i].start()
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
'''
