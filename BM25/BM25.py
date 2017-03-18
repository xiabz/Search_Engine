import math
import operator
import nltk
from bs4 import BeautifulSoup
import string

INDEXPATH = "../../../Given_Corpus_Info/unigram.txt"
DOCUMENTLENGTHPATH = "document_length.txt"
QUERY_FILE_PATH = "cacm_query_token.txt"
REL_JUDGEMENTS_FILE_NAME = "../../../Given_Corpus_Info/cacm.rel.txt"

k1 = 1.2
b = 0.75
k2 = 100
N = 1000
avg = 0

index = {}
simpleIndex = {}
documentLength = {}
nDictionary = {}
relevanceDict = {}

def tokenize(rawHtml):
    soup = BeautifulSoup(rawHtml, 'html.parser')
    rawDocument = soup.getText().encode('utf-8').lower()
    tokens = nltk.word_tokenize(rawDocument)
    for punctuation in string.punctuation:
        tokens = filter(lambda a: a != punctuation, tokens)
    # remove `` manually
    tokens = filter(lambda a: a != "``", tokens)
    # remove '' manually
    tokens = filter(lambda a: a != "''", tokens)
    return tokens

def getRi(queryTerm, queryId):
    if not relevanceDict.has_key(queryId):
        return 0
    relDocList = relevanceDict[queryId]
    invertedList = index[queryTerm]
    count = 0
    for relDocId in relDocList:
        if relDocId in simpleIndex[queryTerm]:
            count += 1
    return count

def getR(queryId):
    if not relevanceDict.has_key(queryId):
        return 0
    return len(relevanceDict[queryId])

def retrieveRelevanceInfo():
    with open(REL_JUDGEMENTS_FILE_NAME, "r") as f:
        for relevanceRecord in f:
            if relevanceRecord == '\n':
                continue
            relevanceRecord = relevanceRecord.strip()
            relevanceItems = relevanceRecord.split(' ')
            queryId = int(relevanceItems[0])
            relDocId = relevanceItems[2]
            if relevanceDict.has_key(queryId):
                relevanceDict[queryId].append(relDocId)
            else:
                relevanceDict[queryId] = [relDocId]

def retrieveIndex():
    with open(INDEXPATH, "r") as f:
        for invertedList in f:
            space = invertedList.find(" ")
            term = invertedList[0:space]
            tfs = invertedList[space + 1:]
            documentList = []
            docIdSet = set()
            b = tfs.split(" ")
            n = 0
            for tf in b:
                if tf == "\n":
                    continue
                a = tf.split(":")
                documentID = a[0]
                frequency = int(a[1])
                item = ( documentID, frequency )
                n += 1
                documentList.append(item)
                docIdSet.add(documentID)
            index[term] = documentList
            simpleIndex[term] = docIdSet
            nDictionary[term] = n

def retrieveDocumentLength():
    global avg
    file = open(DOCUMENTLENGTHPATH, "r")
    for i in range(N):
        s = file.readline().split(" ")
        documentLength[s[0]] = int(s[1])
    s = file.readline()
    avg = int(s)
    file.close()

def parseQueryText(queryText):
    queryDictionary = {}
    for queryTerm in queryText.split(" "):
        if queryTerm in queryDictionary:
            queryDictionary[queryTerm] += 1
        else:
            queryDictionary[queryTerm] = 1
    return queryDictionary

def calculateTermScore(documentID, f, qf, term):
    k = k1 * ((1 - b) + b * documentLength[documentID] / avg)
    ni = nDictionary[term]
    beforeLog = (N - ni) / (ni * 1.0) * (k1 + 1) * f / ((k + f) * 1.0) * (k2 + 1) * qf / ((k2 + qf) * 1.0)
    score = math.log(beforeLog)
    return score

def calculateBM25LScore(qtf, tf, dl, ri, R, ni):
    K = k1 * ((1 - b) + b * (float(dl) / avg))
    binaryModel = float((ri + 0.5) / (R - ri + 0.5)) / ((ni - ri + 0.5)/(N - ni - R + ri + 0.5))
    tfComponent = float((k1 + 1) * tf) / (K + tf)
    qtfComponent = float((k2 + 1) * qtf) / (k2 + qtf)

    return math.log(binaryModel * tfComponent * qtfComponent)



def doQuery(queryID, queryText, file):
    BM25 = {}
    queryDictionary = parseQueryText(queryText)
    print queryID
    for queryTerm in queryDictionary:
        if not index.has_key(queryTerm):
            continue
        invertedList = index[queryTerm]
        R = getR(queryID)
        ri = getRi(queryTerm, queryID)
        for documentID, frequency in invertedList:
            #termScore = calculateTermScore(documentID, frequency, queryDictionary[queryTerm], queryTerm)
            termScore = calculateBM25LScore(queryDictionary[queryTerm], frequency, documentLength[documentID], ri, R, nDictionary[queryTerm])
            if documentID in BM25:
                BM25[documentID] += termScore
            else:
                BM25[documentID] = termScore
    sorted_scores = sorted(BM25.items(), key=operator.itemgetter(1), reverse=True)
    rank = 1
    for documentID, score in sorted_scores:
        queryID = str(queryID)
        file.write(queryID + " Q0 " + documentID + " " + str(rank) + " " + str(score) + " BM25\n")
        rank += 1
        if rank == 101:
            break

if __name__ == '__main__':

    # read index from previous file
    retrieveIndex()
    # read document length information from previous file
    retrieveDocumentLength()
    # read relevance judgements
    retrieveRelevanceInfo()
    # do the query
    
    queryID = 0

    file = open("BM25_Ranking_Result/BM25_Ranking_With_Rel.txt", "w")
    with open(QUERY_FILE_PATH, "r") as f:
        for query in f:
            query = query[0: query.find('\n') - 1]
            print query
            queryID += 1
            doQuery(queryID, query, file)
    file.close()