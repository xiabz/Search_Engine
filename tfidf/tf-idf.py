import operator
import math

INDEXPATH = "unigram_index.txt"
DOCUMENTLENGTHPATH = "document_length.txt"
QUERY_FILE_PATH = "cacm_query_token.txt"

N = 1000

index = {}
nDictionary = {}

def retrieveIndex():
    with open(INDEXPATH, "r") as f:
        for invertedList in f:
            space = invertedList.find(" ")
            term = invertedList[0:space]
            tfs = invertedList[space + 1:]
            documentList = []
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
            index[term] = documentList
            nDictionary[term] = n


def parseQueryText(queryText):
    queryDictionary = {}
    for queryTerm in queryText.split(" "):
        if queryTerm in queryDictionary:
            queryDictionary[queryTerm] += 1
        else:
            queryDictionary[queryTerm] = 1
    return queryDictionary

def calculateTermScore(frequency, n):
    tf = frequency
    idf = math.log(N / (n * 1.0), 10)
    return tf * idf

def doQuery(queryID, queryText, file):
    tfidf = {}
    queryDictionary = parseQueryText(queryText)
    for queryTerm in queryDictionary:
        if queryTerm in index:
            invertedList = index[queryTerm]
        else:
            continue
        for documentID, frequency in invertedList:
            termScore = calculateTermScore(frequency, len(invertedList))
            if documentID in tfidf:
                tfidf[documentID] += termScore
            else:
                tfidf[documentID] = termScore
    sorted_scores = sorted(tfidf.items(), key=operator.itemgetter(1), reverse=True)
    rank = 1
    for documentID, score in sorted_scores:
        queryID = str(queryID)
        file.write(queryID + " Q0 " + documentID + " " + str(rank) + " " + str(score) + " tf*idf\n")
        rank += 1
        if rank == 101:
            break

if __name__ == '__main__':

    # read index from previous file
    retrieveIndex()
    # do the query
    queryID = 0

    file = open("TF-IDF_Ranking_Result/tf-idf.txt", "w")
    with open(QUERY_FILE_PATH, "r") as f:
        for query in f:
            query = query[0: query.find('\n') - 1]
            queryID += 1
            doQuery(queryID, query, file)
    f.close()
    file.close()
    pass