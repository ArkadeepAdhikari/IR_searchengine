import os
import json
from bs4 import BeautifulSoup
import re
from nltk.stem import PorterStemmer
from urllib.parse import urldefrag
import csv

'''
Iterate through files
add entry into doc hashMap - id,url
extract content (<!Doctype Html)
parse using beautiful soup 
Construct Inverted Index - 1GB at a time
Merge Indices   
'''

tagsScoreDict = {'title':9, 'h1':8, 'h2':7, 'h3':6, 'h4':5, 'h5':4, 'h6':3}
ps = PorterStemmer()


def defrag(url):
    return urldefrag(url)[0]


def processText(text):
    finalText = text.replace('\t', ' ')  # Replacing tabs with space 
    finalText = finalText.replace('\n', ' ')  # Replacing new line characters with space
    regex = re.compile('[^a-zA-Z0-9 ]')  # Regex to recognize bad input to remove it
    finalText = regex.sub(' ', finalText)
    regex = re.compile(' [0-9]* ')
    finalText = regex.sub(' ', finalText)
    return finalText


def extractText(content, docId, ngrams, score_dict, anchor_text_file):
    soup = BeautifulSoup(content, features="html.parser")
    
    wordSet = set()
    position = 0
    
    texts = soup.findAll(text=True)
    for element in texts:
        parentElement = element.parent.name
        if parentElement not in ['style', 'script', 'head', 'meta', '[document]']:
            if parentElement in tagsScoreDict.keys():
                position = updateIndex(element.strip(), docId, ngrams, score_dict, wordSet, position, tagsScoreDict[parentElement])
                
    bold_segments = soup.find_all('b')
    finalText = ' '.join([seg.text.strip() for seg in bold_segments])  
    position = updateIndex(finalText, docId, ngrams, score_dict, wordSet, position, 2)           
                
    for element in texts:
        parentElement = element.parent.name
        if parentElement not in ['style', 'script', 'head', 'meta', '[document]'] and parentElement not in tagsScoreDict.keys():
            if parentElement != 'b':
                position = updateIndex(element.strip(), docId, ngrams, score_dict, wordSet, position, 1)      
    
    # anchorText
    for seg in soup.find_all('a'):
        anchor_text = processText(seg.text).strip()
        if anchor_text == '' or anchor_text in ['here', 'home', 'news']: continue
        if 'href' not in seg.attrs.keys(): continue
        url = defrag(seg.attrs['href'])
        if url != '':
            anchor_text_file.write(anchor_text + ' | ' + url + '\n')
    return position


def updateIndex(finalText, docId, ngrams, score_dict, wordSet, position, score):
    finalText = processText(finalText)
    
    stemmedTokens = [ps.stem(token) for token in finalText.split()]
    
    for idx, token in enumerate(stemmedTokens):
        if token.isdigit() : continue
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
            ngram[tok].append(str(docId) + '|' + str(position))
        
        if token not in wordSet:
            if token not in score_dict:
                score_dict[token] = []
            score_dict[token].append(str(docId) + '|' + str(score))
        
        wordSet.add(token)
        position += 1
    return position

        
def getFilename(idx, indexFileCounter): 
    fileName = ''
    if idx == 0: fileName = 'onegram_'
    elif idx == 1: fileName = 'twograms_'
    else: fileName = 'threegrams_'
    fileName = fileName + str(indexFileCounter) + '.txt'
    return fileName


if __name__ == '__main__':
    corpusDir = '/Users/prameela/Desktop/Info Retrieval/DEV/'
    indexFileCounter = 0
    
    ngrams = []
    one_gram = {}
    two_gram = {}
    three_gram = {}
    ngrams = [one_gram, two_gram, three_gram]
    
    score_dict = {}
    doc_dict = {}
    
    urlSet = set()
    header = ['docId', 'url', 'wordcount']
    if(os.path.exists('urlList.csv')):
        listCsv = open('urlList.csv', 'r') 
        listReader = csv.DictReader(listCsv)
        for row in listReader:
            urlSet.add(row['url'])
        urlcounter = len(urlSet)    
        listCsv.close()
    else:
        listCsv = open('urlList.csv', 'w+')
        listWriter = csv.DictWriter(listCsv, fieldnames=header)
        listWriter.writeheader()
        listCsv.close()
    docId = len(urlSet)    
   
    listCsv = open('urlList.csv', 'a')
    listWriter = csv.DictWriter(listCsv, fieldnames=header)
    
    if not os.path.exists('anchortext.txt'):
        anchor_text = open('anchortext.txt', 'w+') 
        anchor_text.close()
    anchor_text_file = open('anchortext.txt', 'a')    
    
    subfolders = [ f.path for f in os.scandir(corpusDir) if f.is_dir() ]
    
    for folder in subfolders:
        for file in os.listdir(folder):
            if file.startswith('.'):
                continue
            with open(folder + '/' + file) as f:
                data = json.load(f)
                url = defrag(data['url'])
                
                if url in urlSet: continue
                
                content = data['content'].lower()
                if 'doctype html' in content[:20] or '<html>' in content[:20]:
                    docId = len(urlSet)
                    numWords = extractText(content, docId, ngrams, score_dict, anchor_text_file)
                    doc_dict[docId] = url + ' | ' + str(numWords)
                    anchor_text_file.flush()
                    urlSet.add(url)
                    entry = {'docId': docId, 'url' : url,
                             'wordcount' : str(numWords)}
                    listWriter.writerow(entry)
                    listCsv.flush()
                    if docId != 0 and docId % 100 == 0 : print(docId)
                    if docId != 0 and docId % 1500 == 0:
                        print('Writing to new index file')
                        for idx, ngram in enumerate(ngrams):
                            filename = getFilename(idx, indexFileCounter)
                            with open(filename, 'w+') as file:
                                file.write("{\n")
                                for i in sorted(ngram.keys()):
                                    file.write(i + ':' + str(ngram[i]))
                                    file.write('\n')
                                file.write("}")
                        with open('scorefile_' + str(indexFileCounter) + '.txt', 'w+') as file:
                            file.write("{\n")
                            for i in sorted(score_dict.keys()):
                                file.write(i + ':' + str(score_dict[i]))
                                file.write('\n')
                            file.write("}")        
                        indexFileCounter += 1 
                        for ngram in ngrams:   
                            ngram.clear()
    print('Finally Writing to new index file')
                        
    for idx, ngram in enumerate(ngrams):
        filename = getFilename(idx, indexFileCounter)
        with open(filename, 'w+') as file:
            file.write("{\n")
            for i in sorted(ngram.keys()):
                file.write(i + ':' + str(ngram[i]))
                file.write('\n')
            file.write("}")
            
    with open('scorefile_' + str(indexFileCounter) + '.txt', 'w+') as file:
        file.write("{\n")
        for i in sorted(score_dict.keys()):
            file.write(i + ':' + str(score_dict[i]))
            file.write('\n')
        file.write("}")
    
    with open('doc_dict.txt', 'w+') as file:
        file.write("{\n")
        for i in doc_dict.keys():
            file.write(str(i) + ':' + str(doc_dict[i]))
            file.write('\n')
        file.write("}") 
    print('Done')      
