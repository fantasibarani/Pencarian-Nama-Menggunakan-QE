# LIBRARY FOR DATA LOADING
import xml.etree.ElementTree as ET

# LIBRARY FOR PREPROCESSING
import string
import re
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
# load

# load
# LIBRARY FOR RANKED RETRIEVAL
import math
from collections import OrderedDict

# PREPROCESSING FUNCTION

def loadData(location):
    data = ET.parse(location)
    return data

def docNumber(location):
    docNo = []
    data = loadData(location)
    for node in data.iter("DOCNO"):
        docNo.append(node.text)
    return docNo

def docHeadline(location):
    docHead = []
    data = loadData(location)
    for node in data.iter("HEADLINE"):
        docHead.append(node.text)
    return docHead
    
def docText(location):
    docText = []
    data = loadData(location)
    for node in data.iter("TEXT"):
        docText.append(node.text)
    return docText
    
def removePunctuation(textList):
    for i in range(len(textList)):
        for punct in string.punctuation:
            textList[i] = textList[i].replace(punct, " ")
        textList[i] = re.sub(r'^https?:\/\/.*[\r\n]*', '', textList[i], flags=re.MULTILINE)
    return textList

def caseFolding(textList):
    text = []
    for i in range(len(textList)):
        text.append(textList[i].lower())
    return text

def token(sentence):
    token = []
    for word in CountVectorizer().build_tokenizer()(sentence):
        token.append(word)
    return token

def tokenize(textList):
    tokens = []
    for i in range(len(textList)):
        tokens.append(token(textList[i]))
    return tokens

def checkStopword(sentence, stop_words):
    sentence = [w for w in sentence if not w in stop_words]
    return sentence
    
def stopwordRemove(textList):
    stop_words = set(stopwords.words('english'))
    text = []
    for i in range(len(textList)):
        text.append(checkStopword(textList[i], stop_words))
    return text

def numberRemove(textList):
    text = []
    for i in range(len(textList)):
        text.append([w for w in textList[i] if not any(j.isdigit() for j in w)])
    return text

def stemming(textList):
    stemmer = PorterStemmer()
    text = textList
    for i in range(len(textList)):
        for j in range(len(textList[i])):
            text[i][j] = stemmer.stem(text[i][j])
    return text

def sorting(textList):
    for i in range(len(textList)):
        textList[i] = sorted(textList[i])
    return textList

def getAllTerms(textList):
    terms = []
    for i in range(len(textList)):
        for j in range(len(textList[i])):
            terms.append(textList[i][j])
    return sorted(set(terms))

# INDEXING FUNCTION

def createIndex(textList, docno):
    terms = getAllTerms(textList)
    proximity = {}
    for term in terms:
        position = {}
        for n in range(len(textList)):
            if(term in textList[n]):
                position[docno[n]] = []
                for i in range(len(textList[n])):
                    if(term == textList[n][i]):
                        position[docno[n]].append(i)
        proximity[term] = position
    return proximity

def exportIndex(index, filename):
    file = open(filename,'w')
    for n in index:
        file.write(n+'\n')
        for o in index[n]:
            file.write('\t'+o+': ')
            for p in range(len(index[n][o])):
                file.write(str(index[n][o][p]))
                if(p<len(index[n][o])-1):
                    file.write(', ')
                else:
                    file.write('\n')
    file.close()
    return "Index's file has been successfully created."


# RANKED RETRIEVAL FUNCTION
def queryInIndex(query, index):
    result = []
    for word in query:
        if word in index:
            result.append(word)
    return result

def df(query, index):
    docFreq = {}
    for word in query:
        if word in index:
            docFreq[word] = len(index[word])
    return docFreq

def idf(df, N):
    inv = {}
    for word in df:
        inv[word] = math.log10(N/df[word])
    return inv

def tf(query, index):
    termFreq = {}
    for word in query:
        freq = {}
        if word in index:
            for i in index[word]:
                freq[i] = len(index[word][i])
        termFreq[word] = freq
    return termFreq

def tfidf(tf, idf):
    w = {}
    for word in tf:
        wtd = {}
        for doc in tf[word]:
            wtd[doc] = (1+(math.log10(tf[word][doc])))*idf[word]
        w[word] = wtd
    return w
    
def score(TFIDF):
    res = {}
    for i in TFIDF:
        for j in TFIDF[i]:
            res[j] = 0
    for i in TFIDF:
        for j in TFIDF[i]:
            res[j] = res[j]+TFIDF[i][j]
    sorted_dict = sorted(res, key=res.get, reverse=True)
    return sorted_dict

# EXPANSION
def notRelevance(rel, docsNumber):
    notRelevanceNumber = []
    for i in docsNumber:
        if int(i) not in (rel):
            notRelevanceNumber.append(int(i))
    return notRelevanceNumber

def getIndex(docs, docsNumber):
    res = []
    for i in docs:
        res.append(docsNumber.index(str(i)))
    return res

def vector(text ,terms):
    Vec = []
    for i in range(len(terms)):
        if(terms[i] in text):
            Vec.append(1)
        else:
            Vec.append(0)
    return Vec

def expansion(query, relevan, irrelevan, a, b, c):
    result = {}
    exp    = []
    irrel  = irrelevan[0]
    rel    = relevan[0]
    b      = b / len(relevan)
    c      = c / len(irrelevan)
    
    for i in range(1,len(relevan)):
        for j in range(len(relevan[i])):
            rel[j] = rel[j] + relevan[i][j]
            irrel[j] = irrel[j] + irrelevan[i][j]
            
    for i in range(len(rel)):
        rel[i] = b*rel[i]
        irrel[i] = c*irrel[i]
        query[i] = a*query[i]
        
    for i in range(len(rel)):
        exp.append(query[i]+rel[i]-irrel[i])
        
    for i in range(len(exp)):
        if(exp[i]>0):
            result[i] = exp[i]
        
    return result

