# -*- coding: utf-8 -*-
'''
    File to get data from files. Simply call the following.
    getAllData(['guanAbstracts.txt', 'tsueAbstracts.txt'])
    Input
            fileNameList            List of the file names/path to files containing
                                    the title and abstract
    Output
            publications            List of publications objects contained in
                                    fileNameList
                                    For more information on the Publication object,
                                    see Publication.py
'''
import codecs
import re
from Publication import Publication
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import find
from stemming.porter2 import stem

skipTerms = {
    'Collaborators',
    'Author information',
    'Erratum in',
    'Comment in',
    'Update in',
    'Comment on',
    'Comment in',
    'Update of',
    'Summary for patients in',
    'Retraction in',
    'Expression of concern in'}
idTerms = {'DOI', 'PMCID', 'PMID'}

def getNextEntry(f, line, skipTerms = set(), startTerms = idTerms):
    while line != '\n':
        for term in startTerms:
            if line.startswith(term):
                return line
        line = f.readline()
    while line == '\n':
        line = f.readline()
    while True:
        hasSkipped = False
        for term in skipTerms:
            if line.startswith(term):
                line = getNextEntry(f, line)
                hasSkipped = True
                break
        if not hasSkipped:
            break
    return line

def getBlock(f, line, stopAtPeriod = False, stopAtStartTerms = set()):
    block = u''
    while line != '\n':
        for term in stopAtStartTerms:
            if line.startswith(term):
                return block, line
        if stopAtPeriod and line[-2] == '.':
            return block + line[:-2], f.readline()
        block = block + line.replace('\n', '') + ' '
        line = f.readline()
    if block != '':
        return block[:-1], line
    return block, line

def getDataFromNonJournalEntry(f, line, titleBlock):
    title = re.sub('(^\d*\.\s)', '', titleBlock)
    line = getNextEntry(f, line)
    authors, line = getBlock(f, line, stopAtPeriod = True)
    date, line = getBlock(f, line)
    line = getNextEntry(f, line, skipTerms)
    abstract, line = getBlock(f, line, stopAtStartTerms = idTerms)
    line = getNextEntry(f, line, skipTerms = set(['Publisher']), startTerms = idTerms)
    pmid = None
    while line != '\n':
        splitLine = line.split()
        if splitLine[0] == 'PMID:':
            pmid = splitLine[1]
        line = f.readline()

    return title, abstract, date, authors, pmid

def getDataFromJournalEntry(f, line, dateBlock):
    date = dateBlock
    line = getNextEntry(f, line)
    title, line = getBlock(f, line)
    line = getNextEntry(f, line)
    if line[0] == '[' and 'No authors listed' not in line:
        line = getNextEntry(f, line)
    authors, line = getBlock(f, line)
    line = getNextEntry(f, line, skipTerms)
    abstract, line = getBlock(f, line)
    line = getNextEntry(f, line)
    if not (line.startswith('DOI') or line.startswith('PMID') or line.startswith('PMCID')):
        line = getNextEntry(f, line)
    pmid = None
    # Get PMID
    while line != '\n':
        splitLine = line.split()
        if splitLine[0] == 'PMID:':
            pmid = splitLine[1]
        line = f.readline()
    return title, abstract, date, authors, pmid


# Get data from individual entry
def getDataFromEntry(f, line):
    firstBlock, line = getBlock(f, line)
    if 'RETRACTED ARTICLE' in firstBlock:
        return None
    parsedDateVector = re.findall('((19|20)[0-9]{2}\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))', firstBlock)
    if len(parsedDateVector) is 0:
        parsedDateVector = re.findall('((19|20)[0-9]{2})', firstBlock)
    if len(parsedDateVector) is 0:
        title, abstract, date, authors, pmid = getDataFromNonJournalEntry(f, line, firstBlock)
    else:
        title, abstract, date, authors, pmid = getDataFromJournalEntry(f, line, firstBlock)

    cleanedAuthors = re.sub('[0-9()]', '', authors).split(', ')
    parsedDateVector = re.findall('((19|20)[0-9]{2}\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))', date)
    if len(parsedDateVector) is 0:
        parsedDateVector = re.findall('((19|20)[0-9]{2})', date)
    if len(parsedDateVector) is 0:
        print('Error: No date found for paper', date)
        parsedDate = None
    else:
        parsedDate = parsedDateVector[0][0]
    return Publication(title, abstract, parsedDate, cleanedAuthors, pmid)


# Function to read in the data from the file
def getFileData(fileName):
    publications = []
    line = '\n'
    with codecs.open(fileName, encoding='utf8') as f:
        while line == '\n':
            line = f.readline()
        lastEntry = 0
        numLoops = 0
        numSkipped = 0
        while True:
            numLoops += 1
            # Go to next entry
            while True:
                if len(line) == 0:
                    break
                if len(re.findall('^' + str(lastEntry + 1) + '\.\s', line)) > 0: break
                line = f.readline()

            if len(line) == 0: break
            result = getDataFromEntry(f, line)
            if result != None:
                publications.append(result) #Removes the retracted articles
            else:
                numSkipped += 1
            lastEntry += 1
        print('Number of loops: %d' % numLoops)
        print('Number skipped: %d' % numSkipped)
        f.close()
    return publications

def stemAbstract(abstract):
    vectorAbstract = abstract.split()
    returnString = ''
    for i in range(len(vectorAbstract)):
        returnString += stem(vectorAbstract[i]) + ' '
    return returnString


def getAllData(fileNameList):
    '''
    Given a list of fileNames and the name of the vector type ('tfidf', 'count'),
    returns a dict of key=title and value=dict-vector of papers and also a list of
    lists, where each nested list contains all the titles of the papers belonging to
    a single author
    '''
    publications = []
    for fileName in fileNameList:
        publications += getFileData(fileName)

    print('Total Number Papers: ', len(publications))
    abstracts = []
    for i in range(len(publications)):
        stemmedAbstract = stemAbstract(publications[i].abstract)
        publications[i].stemmedAbstract = stemmedAbstract
        # Test for performance of stemming
        abstracts.append(stemmedAbstract)
        # abstracts.append(publications[i].abstract)
    print('Vectorizing Papers')
    tfIdfVectorizer = TfidfVectorizer()
    tfIdfMatrix = tfIdfVectorizer.fit_transform(abstracts)
    countVectorizer = CountVectorizer()
    countMatrix = countVectorizer.fit_transform(abstracts)
    for i in range(len(publications)):
        tfRow, tfCol, tfValue = find(tfIdfMatrix[i])
        publications[i].abstractTfidfVector = {col: value for col, value in zip(tfCol, tfValue)}
        ctRow, ctCol, ctValue = find(countMatrix[i])
        publications[i].abstractCountVector = {col: value for col, value in zip(ctCol, ctValue)}
    print('Vectorized Papers')


    return publications
