import os
import csv
from PartA import tokenize
import itertools
from urllib.parse import urldefrag
from urllib.parse import urlparse
import pprint


def mostfrequentwords():    
    contentDir = '/Users/prameela/contentDir'
    freqs = {}
    stopwords = set()
    stopwordscsv = open('/Users/prameela/stopwords.csv', 'r')
    csvReader = csv.DictReader(stopwordscsv)
    for row in csvReader:
        stopwords.add(row['word'])
    stopwordscsv.close()
    for txtfile in os.listdir(contentDir):
        filename = contentDir + '/' + txtfile
        freqs = dict(tokenize(filename, stopwords, freqs))
    out = dict(itertools.islice(freqs.items(), 50))
    print(out)
    print('###### Keys #######')
    print(out.keys())

    
def subDomains():
    domainMap = {}
    listCsv = open('/Users/prameela/urlList.csv', 'r') 
    listReader = csv.DictReader(listCsv)
    for row in listReader:
        url = urldefrag(row['url'])[0]
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname.endswith('ics.uci.edu'):
            continue
        if hostname in domainMap:
            domainMap[hostname] += 1
        else:
            domainMap[hostname] = 1
    listCsv.close()
    print(len(domainMap))
    for key in sorted(domainMap.keys()):
        print("%s: %s" % (key, domainMap[key]))
        
    
if __name__ == '__main__':
#     mostfrequentwords()
    subDomains()    
        
