from bs4 import BeautifulSoup
import nltk
import string

QUERY_FILE_PATH = '../../../Given_Corpus_Info/cacm.query.txt'
QUERY_TOKEN_FILE_PATH = 'cacm_query_token.txt'

def queryTokenize():
    f = open(QUERY_FILE_PATH, 'r')
    fw = open(QUERY_TOKEN_FILE_PATH, 'w')
    context = f.read()
    soup = BeautifulSoup(context, 'html.parser')
    for tag in soup.find_all('docno'):
        tag.replaceWith('')
    queries = soup.find_all('doc')
    for query in queries:
        query = query.getText().encode('utf-8').lower()
        tokens = nltk.word_tokenize(query)
        for punctuation in string.punctuation:
            tokens = filter(lambda a: a != punctuation, tokens)
        # remove `` manually
        tokens = filter(lambda a: a != "``", tokens)
        # remove '' manually
        tokens = filter(lambda a: a != "''", tokens)
        for token in tokens:
            fw.write(token + ' ')
        fw.write('\n')
    fw.close()
    f.close()

if __name__ == '__main__':

    queryTokenize()

    pass