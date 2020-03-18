'''
This implements the search for our search engine
'''

from IndexBuilder import processText
from nltk.stem import PorterStemmer
import threading
from IndexHasher import getgroup
import os
import pickle
import queue
from collections import Counter
import time
import csv
from functools import cmp_to_key

ps = PorterStemmer()

doc_dict = {}

three_grams, two_grams, one_grams = {}, {}, {}
ngrams = [one_grams, two_grams, three_grams]
scores = {}

ngrams_dict = [dict(), dict(), dict()]
ngrams_occur_freq = [list(), list(), list()]
mostcommon = [set(), set(), set()]

tfidf = {}


def scorefunc(q, term):
    filename = 'scores/'
    filename += term[0]
    length = len(term)
    for p in range(4):
        if p + 1 <= length - 1:
            filename += '_' + str(getgroup(term[p + 1]) + 1)
        else:
            filename += '_' + '1'
    filename += '.pickle'
    
    if (os.path.exists(filename)):
        with open(filename, 'rb') as handle:
            mydict = pickle.load(handle)
            if term in mydict:
                q.put((True, 1, term, [], mydict[term][:-1].strip('[]').split(', ')))


def searchfunc(q, term, n):
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
    
    if (os.path.exists(filename)):
        with open(filename, 'rb') as handle:
            mydict = pickle.load(handle)
            if mydict.get(term, None):
                val = (mydict[term][:-1].strip('[]').replace(',', '|' + term + ',') + '|' + term).split(', ')
                q.put((False, n - 1, term, val, []))
    

def append_to_ngrams_list(q, val_list_i, i):
    l = []
    for x in val_list_i:
        if x.split('|', 1)[0].strip("'") in mostcommon[i]:
            my_list = []
            terms = x.split('|')
            my_list.append(int(terms[0].strip("'")))
            my_list.append(int(terms[1].strip("'")))
            my_list.append(terms[2])
            l.append(my_list)
    q.put((i, l))
    return


def sortbyoccurence(q, ng_dict, i):
    val_list = []
    for x in ng_dict.values():
        val_list += x
    resp_id = Counter([x.split('|', 1)[0] for x in val_list])
    my_mostcommon = set([x[0].strip("'") for x in resp_id.most_common((15))])  # stores a tuple of (docId, count) for corresponding n_gram
    q.put((i, val_list, my_mostcommon))
    
    return


def scores_filter(q, term, mostcommondocs):
    term_dict = {}
    if term not in scores: return
    for score in scores[term]:
        doc_id = score.split('|')[0]
        if doc_id in mostcommondocs:
            term_dict[doc_id] = float(score.split('|')[1])
    q.put((term, term_dict))        


def get_urls_from_ids():
    doc_dict.clear()
    listCsv = open('urlList.csv', 'r') 
    listReader = csv.DictReader(listCsv)
    for row in listReader:
        doc_dict[row['docId']] = row['url']    
    listCsv.close()


def compare(val1, val2):
    if val1[0] != val2[0]:
        return val1[0] - val2[0]
    elif val1[1] != val2[1]:
        return val1[1] - val2[1]
    else: return 0
    
    
def doc_splitter(doc_list):
    curr_doc_id = -1
    i = -1
    doc_pos = [[] for _ in range(15)] 
    for val in doc_list:
        if val[0] != curr_doc_id:
            i = i + 1
            curr_doc_id = val[0]
        doc_pos[i].append(val)
    return doc_pos


def get_doc_score(q4, my_doc_pos, n):
    if len(my_doc_pos) == 0 : return
        
    doc_id = str(my_doc_pos[0][0])
    terms = set()
    total_terms = len(ngrams[n].keys())
    
    length = len(my_doc_pos) - 1
    
    pos_score = 0
    
    for idx, val in enumerate(my_doc_pos):
        terms.add(val[2])
        for i in range(3):
            if idx + i <= length:
                pos1 = min(ngrams[n][val[2]])
                pos2 = max(ngrams[n][my_doc_pos[idx + i][2]])
                if pos1 < pos2 : pos_score += 1
    
    total_tfidf = 0  
    
    for term in terms:
        for one_gram in term.split(' '):
            total_tfidf += float(tfidf[one_gram][doc_id])
    
    score = (len(terms) * 1.0 / total_terms) * (pos_score * 1.0 / len(my_doc_pos)) * total_tfidf * (n + 1) * (n + 1) 
    
    q4.put((doc_id, score))
    return 


def sort_and_split_docs(q3, n):
    doc_list = ngrams_occur_freq[n]
    doc_list = sorted(doc_list, key=cmp_to_key(compare))
    # split docs
    doc_pos = doc_splitter(doc_list)
    q3.put((n, doc_pos))
    return


def initialize():
    scores.clear()
    
    for i in range(3):
        ngrams[i].clear()
        ngrams_dict[i].clear()
        ngrams_occur_freq[i].clear()
        mostcommon[i].clear()
    
    tfidf.clear()


def final_processing(term):
    o_term = term
    initialize()
    
    start = time.time()
    # Processing
    term = processText(term)

    stemmedTokens = [ps.stem(token) for token in term.split()]
    min_n = min(3, len(stemmedTokens))

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

    # 5 threads for onegrams, 6 for twograms, 7 for threegrams
    d = {}
    q_ng = queue.Queue()
    for i in range(len(three_grams.keys())):
        d[i % 5] = threading.Thread(target=searchfunc, args=(q_ng, list(three_grams.keys())[i], 3))
        d[i % 5].start()
    for i in range(len(two_grams.keys())):
        d[5 + (i % 6)] = threading.Thread(target=searchfunc, args=(q_ng, list(two_grams.keys())[i], 2))
        d[5 + (i % 6)].start()
    for i in range(len(one_grams.keys())):
        d[11 + (i % 7)] = threading.Thread(target=searchfunc, args=(q_ng, list(one_grams.keys())[i], 1))
        d[11 + (i % 7)].start()
    for i in range(len(one_grams.keys())):
        d[18 + (i % 7)] = threading.Thread(target=scorefunc, args=(q_ng, list(one_grams.keys())[i]))
        d[18 + (i % 7)].start()
    for i in d :
        d[i].join() 
    while not q_ng.empty():
        hasScore, pos, term, val, score_val = q_ng.get()
        if hasScore:
            scores[term] = score_val
        else:
            ngrams_dict[pos][term] = val 

    ng = {}
    val_list = [list(), list(), list()] 
    q = queue.Queue()
    
    for i in range(min_n):
        ng[i] = threading.Thread(target=sortbyoccurence, args=(q, ngrams_dict[i], i))
        ng[i].start()
        
    for i in ng:
        ng[i].join() 
    while not q.empty() : 
        pos, my_val_list, my_mostcommon = q.get()
        val_list[pos] = my_val_list
        mostcommon[pos] = my_mostcommon 

    q2 = queue.Queue()
    
    v = {}
    for i in range(min_n):
        v[i] = threading.Thread(target=append_to_ngrams_list, args=(q2, val_list[i], i))
        v[i].start()

    for i in v:
        v[i].join()
    while not q2.empty():
        pos, my_ngrams_occu_freq = q2.get()
        ngrams_occur_freq[pos] = my_ngrams_occu_freq

    time_1 = time.time() - start

    doc_pos = [list(), list(), list()]
    
    # 3 threads
    v = {}
    q3 = queue.Queue()
    for i in range(min_n):
        v[i] = threading.Thread(target=sort_and_split_docs, args=(q3, i))
        v[i].start()
    for i in v:
        v[i].join()
    while not q3.empty():
        pos, my_doc_pos = q3.get()
        doc_pos[pos] = my_doc_pos
    
    final_score = {}
    time_2 = time.time() - start
    
    q5 = queue.Queue()
    # 7 threads for onegram scores
    d = {}
    doclist = mostcommon[0].union(mostcommon[1]).union(mostcommon[2])
    for i in range(len(one_grams.keys())):
        d[i % 7] = threading.Thread(target=scores_filter, args=(q5, list(one_grams.keys())[i], doclist))
        d[i % 7].start()
    for i in d:
        d[i].join()
    while not q5.empty():
        term, my_tfidf = q5.get()
        tfidf[term] = my_tfidf
    
    # max of 45 threads
    v.clear()
    q4 = queue.Queue()
    for i in range(min_n):
        for p in range(len(doc_pos[i])):
            v[i * 15 + p] = threading.Thread(target=get_doc_score, args=(q4, doc_pos[i][p], i))
            v[i * 15 + p].start()
    for i in v:
        v[i].join()
    while not q4.empty():
        doc_id, doc_score = q4.get()
        if doc_id not in final_score:
            final_score[doc_id] = 0
        final_score[doc_id] += doc_score
        
    time_3 = time.time() - start
    sorted_scores = sorted(final_score.items(), key=lambda x: x[1], reverse=True)
    
    num_results = 10    # we display only top 10 links according to scores
    if len(sorted_scores) < num_results : num_results = len(sorted_scores)
    url_list = []
    for i in range(num_results):
        url_list.append(doc_dict[str(sorted_scores[i][0])])
    time_total = str(time.time() - start)
    print(time_1, time_2, time_3, time_total)
    return(url_list, time_total)


if __name__ == '__main__':
    get_urls_from_ids();
    urls, timet = final_processing("Master of Computer Science")  # Query to be searched
    print(urls)
    print(timet)
