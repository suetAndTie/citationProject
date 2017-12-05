# -*- coding: utf-8 -*-
'''
    File to get data from files. Simply call the following.
    getAllData(['guanAbstracts.txt', 'tsueAbstracts.txt'], 'tfidf')

    Input
            fileNameList            List of the file names/path to files containing
                                    the title and abstract
            vectorTypeName          Name of the type of vector to be used.
                                    Currently, either 'tfidf' or 'count'
    Output
            finalVectorDict         Dict with key=title and value=dict vector
                                    with key=wordNumber and value=wordUsage
            authorPapersList        List of lists, where each nested list contains
                                    all the paper titles for a given author.
'''
import codecs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import find
import re




# Dict of the key=name of vector type and value=construct of vector
VECTOR_TYPES = {
    'tfidf':TfidfVectorizer,
    'count':CountVectorizer
}


def getRawData(fileName):
    '''
    This function takes in a filename/path-to-file and returns a dict with key=articleTitle
    and value=articleAbstract. It also returns a list of the the article titles, for
    the given author
    '''
    # Step over part of entry
    def stepOver(f, line):
        while line != '\n':
            line = f.readline()
        line = f.readline()
        return line

    # Get data from individual entry
    def getDataFromEntry(f, line):
        title = u''
        abstract = u''
        date = u''
        authors = u''
        pmid = u''
        # Get date line - uncleaned
        while line != '\n':
            # Add on line removing \n at end
            date = date + line[:-1]
            line = f.readline()
        if 'RETRACTED ARTICLE' in date:
            return ''
        line = f.readline()

        # Get title
        while line != '\n':
            # print line
            # Add on line removing \n at end
            title = title + line[:-1]
            line = f.readline()
        line = f.readline()

        if line[0] == '[':
            line = stepOver(f, line)

        # Get authors - uncleaned
        while line != '\n':
            authors = authors + line[:-1]
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

        # if line[:18] == 'Author information':
        #     line = stepOver(f, line)

        # if line[:10] == 'Erratum in':
        #     line = stepOver(f, line)

        # if line[:10] == 'Comment in':
        #     line = stepOver(f, line)

        # if line[:9] == 'Update in':
        #     line = stepOver(f, line)

        # if line[:10] == 'Comment on':
        #     line = stepOver(f, line)

        # line = stepOver(f, line)

        # Get abstact
        while line != '\n':
            # Add on line removing \n at end
            abstract = abstract + line[:-1]
            line = f.readline()

        while line == '\n':
            line = f.readline()
        # copyrightTerms = {
        #     '(C)',
        #     'Copyright',
        #     '(c)',
        #     'Elsevier Science'
        # }
        # for term in copyrightTerms:
        #     if term in line:
        #         line = stepOver(f, line)

        if not (line.startswith('DOI') or line.startswith('PMID') or line.startswith('PMCID')):
            line = stepOver(f, line)


        # if not line[0].isalpha():
        #     line = stepOver(f, line)
        # if line[:9] == 'Copyright':
        #     line = stepOver(f, line)
        # Get PMID
        foundId = False
        while line != '\n':
            # Add on line removing \n at end
            splitLine = line.split()
            if splitLine[0] == 'PMID:':
                pmIds[title] = splitLine[1]
                foundId = True
            line = f.readline()
        # if not foundId:
        #     print('Id not found for %s' % title)
        # Add to papers with title=key and abstract=value
        paperAbstracts[title] = abstract
        cleanedAuthors = re.sub('[0-9()]', '', authors).split(', ')
        paperAuthors[title] = set(cleanedAuthors)
        parsedDateVector = re.findall('((19|20)[0-9]{2}\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))', date)
        if len(parsedDateVector) is 0:
            parsedDateVector = re.findall('((19|20)[0-9]{2})', date)
        if len(parsedDateVector) is 0:
            print('Error: No date found for paper', date)
        else:
            paperDates[title] = parsedDateVector[0][0]
            if not parsedDateVector[0][0].startswith('20'):
                print parsedDateVector[0][0]

        return line


    # Function to read in the data from the file
    def getFileData(fileName):
        exitBool = False
        with codecs.open(fileName, encoding='utf8') as f:
            line = f.readline()
            line = f.readline()
            lastEntry = 0
            while True:
                # Go to next entry
                while True:
                    if len(line) == 0:
                        exitBool = True
                        break
                    if len(re.findall('^' + str(lastEntry + 1) + '\.\s', line)) > 0: break
                    line = f.readline()

                if len(line) == 0: break
                # line is now on beginning of entry, so get data
                line = getDataFromEntry(f, line)
                lastEntry += 1

            f.close()

    paperAbstracts = {}
    paperAuthors = {}
    paperDates = {}
    pmIds = {}
    getFileData(fileName)
    # papers is a dict of key=title to value=abstract
    # the returned list is the list of the key=title for the given author
    return paperAbstracts, paperAuthors, paperDates, list(paperAbstracts), pmIds


def makeVectors(allPapersDict, vectorizerConstructor):
    '''
    Given the dict of key=title value=abstract for all papers
    and the name of the type of vector ('tfidf', 'count'),
    makes the vectors to represent the papers
    '''
    vectorizer = vectorizerConstructor()
    orderedTitles = []
    orderedAbstracts = []
    finalVectorDict = {}


    # Order must be kept, so we iterate over each element
    for key, value in allPapersDict.items():
        orderedTitles.append(key)
        orderedAbstracts.append(value)

    vectorMatrix = vectorizer.fit_transform(orderedAbstracts)
    for i in range(vectorMatrix.shape[0]):
        rowList, colList, valueList = find(vectorMatrix[i])
        finalVectorDict[orderedTitles[i]] = {col:value for col, value in zip(colList, valueList)}


    return finalVectorDict


def getAllData(fileNameList, vectorTypes):
    '''
    Given a list of fileNames and the name of the vector type ('tfidf', 'count'),
    returns a dict of key=title and value=dict-vector of papers and also a list of
    lists, where each nested list contains all the titles of the papers belonging to
    a single author
    '''
    # if vectorTypeName not in VECTOR_TYPES:
    #     errorString = "Not a valid vector type. Must be string of the following: " + str(VECTOR_TYPES.keys())
    #     raise Exception(errorString)

    allPaperAbstractsDict = {}
    allPaperAuthorsDict = {}
    allPaperDatesDict = {}
    allPmIds = {}
    authorPapersList = []
    finalVecs = []
    for fileName in fileNameList:
        paperAbstracts, paperAuthors, paperDates, authorPapers, pmIds = getRawData(fileName)
        allPaperAbstractsDict.update(paperAbstracts)
        allPaperAuthorsDict.update(paperAuthors)
        allPaperDatesDict.update(paperDates)
        allPmIds.update(pmIds)
        authorPapersList.append(authorPapers)

    for vecType in vectorTypes:
        finalVecs.append(makeVectors(allPaperAbstractsDict, VECTOR_TYPES[vecType]))
    return finalVecs, authorPapersList, allPaperAuthorsDict, allPaperDatesDict, allPmIds


# print getAllData(['guanAbstracts.txt'], 'count')
# print getAllData(['tsueAbstracts.txt'], 'tfidf')
