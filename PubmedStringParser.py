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

# Get data from individual entry
def getDataFromEntry(f, line):

    # Step over part of entry
    def stepOver(f, line):
        while line != '\n':
            line = f.readline()
        line = f.readline()
        return line

    title = ''
    abstract = u''
    date = ''
    authors = u''
    pmid = ''
    # Get date line - uncleaned
    while line != '\n':
        date = date + line[:-1] + ' '
        line = f.readline()
    if 'RETRACTED ARTICLE' in date:
        return ''
    line = f.readline()

    # Get title
    while line != '\n':
        title = title + line[:-1] + ' '
        line = f.readline()
    line = f.readline()

    if line[0] == '[':
        line = stepOver(f, line)

    # Get authors - uncleaned
    while line != '\n':
        authors = authors + line[:-1] + ' '
        line = f.readline()
    line = f.readline()

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
    while True:
        hasSkipped = False
        for term in skipTerms:
            if line.startswith(term):
                line = stepOver(f, line)
                hasSkipped = True
                break
        if not hasSkipped:
            break

    # Get abstact
    while line != '\n':
        abstract = abstract + line[:-1] + ' '
        line = f.readline()

    while line == '\n':
        line = f.readline()

    if not (line.startswith('DOI') or line.startswith('PMID') or line.startswith('PMCID')):
        line = stepOver(f, line)

    # Get PMID
    while line != '\n':
        splitLine = line.split()
        if splitLine[0] == 'PMID:':
            pmid = splitLine[1]
        else:
            pmid = None
        line = f.readline()

    # Add to papers with title=key and abstract=value
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
    with codecs.open(fileName, encoding='utf8') as f:
        line = f.readline()
        line = f.readline()
        lastEntry = 0
        while True:
            # Go to next entry
            while True:
                if len(line) == 0:
                    break
                if len(re.findall('^' + str(lastEntry + 1) + '\.\s', line)) > 0: break
                line = f.readline()

            if len(line) == 0: break
            result = getDataFromEntry(f, line)
            if result != '': publications.append(result) #Removes the retracted articles
            lastEntry += 1

        f.close()
    return publications

def stemAbstract(abstract):
    vectorAbstract = abstract.split()
    returnString = ''
    for i in xrange(len(vectorAbstract)):
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

    print 'Total Number Papers: ', len(publications)
    abstracts = []
    for i in xrange(len(publications)):
        stemmedAbstract = stemAbstract(publications[i].abstract)
        publications[i].stemmedAbstract = stemmedAbstract
        # Test for performance of stemming
        abstracts.append(stemmedAbstract)
        # abstracts.append(publications[i].abstract)
    tfIdfVectorizer = TfidfVectorizer()
    tfIdfMatrix = tfIdfVectorizer.fit_transform(abstracts)
    countVectorizer = CountVectorizer()
    countMatrix = countVectorizer.fit_transform(abstracts)
    for i in xrange(len(publications)):
        tfRow, tfCol, tfValue = find(tfIdfMatrix[i])
        publications[i].abstractTfidfVector = {col: value for col, value in zip(tfCol, tfValue)}
        ctRow, ctCol, ctValue = find(countMatrix[i])
        publications[i].abstractCountVector = {col: value for col, value in zip(ctCol, ctValue)}


    return publications
