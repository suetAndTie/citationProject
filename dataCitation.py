import PubmedStringParser
import os.path
import pickle
import concurrent.futures
import Publication
import constants
import util
import numpy as np

def getCitation(inputFiles, labelOutputFile, listStartIndex):
    if os.path.isfile('pubList' + labelOutputFile):
        with open('pubList' + labelOutputFile, 'rb') as f:
            publicationList = pickle.load(f)
    else:
        publicationList = PubmedStringParser.getAllData(inputFiles)
        with open('pubList' + labelOutputFile, 'wb') as f:
            pickle.dump(publicationList, f)

    startIndex = constants.NUM_PAPERS_CITATION * listStartIndex
    if startIndex >= len(publicationList):
        print('List index is %s' %str(listStartIndex))
        raise Exception('Start index %s is too large for publication list of %s and %s number of citations' %(str(startIndex), \
                                                                        str(len(publicationList)), str(constants.NUM_PAPERS_CITATION)))

    if listStartIndex + constants.NUM_PAPERS_CITATION >= len(publicationList):
        listEndIndex = len(publicationList)
    else:
        listEndIndex = listStartIndex + constants.NUM_PAPERS_CITATION
    currList = publicationList[listStartIndex:listEndIndex]
    for i in range(len(currList)):
        currList[i].genRetrospectiveCitations()
        currList[i].getCitedByPMCitations()
    with concurrent.futures.ThreadPoolExecutor(max_workers = constants.MAX_WORKERS) as executor:
        future_to_article = {executor.submit(currList[i].genCitedBy): currList[i].title for i in range(len(currList))}
        for future in concurrent.futures.as_completed(future_to_article):
            articleTitle = future_to_article[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (articleTitle, exc))
            else:
                print('Graph retrieved for %s' % articleTitle)
                if data is None:
                    print('But the data is none')
                else:
                    print(data)
    with open(str(listStartIndex) + 'temp' + labelOutputFile, 'wb') as f:
        pickle.dump(currList, f)

    print('Total pub list length is %s' %str(len(publicationList)))
    print('Curr pub list length is %s' %str(len(currList)))
    print('Number of citations %s' %str(constants.NUM_PAPERS_CITATION))
    print('Actual start index is %s' %str(startIndex))
    print('List index is %s' %str(listStartIndex))
    print('Max list index is %s' %str(len(publicationList)/constants.NUM_PAPERS_CITATION))


# After running getCitation for all of the publications, this function will replace
# the original publist with the new entries
# Puts the final pubList into finalpubList file
def replacePublications(labelOutputFile):
    if os.path.isfile('pubList' + labelOutputFile):
        with open('pubList' + labelOutputFile, 'rb') as f:
            publicationList = pickle.load(f)
    else:
        publicationList = PubmedStringParser.getAllData(inputFiles)
        with open('pubList' + labelOutputFile, 'wb') as f:
            pickle.dump(publicationList, f)

    maxIndex = len(publicationList)/constants.NUM_PAPERS_CITATION
    finalPubList = []
    for startIndex in range(maxIndex + 1):
        with open(str(startIndex) + 'temp' + labelOutputFile, 'rb') as f:
            currPubList = pickle.load(f)
        endIndex = startIndex + len(currPubList)
        finalPubList[startIndex:endIndex] = currPubList
    with open('temp' + labelOutputFile, 'wb') as f:
        pickle.dump(finalPubList, f)

    numScholar = 0
    numPM = 0
    numBoth = 0
    numEither = 0
    for i in range(len(finalPubList)):
        gotScholar = False
        gotPM = False
        if finalPubList[i].citedBy is not None and len(finalPubList[i].citedBy) > 0:
            numScholar += 1
            gotScholar = True
        if finalPubList[i].PMCitedBy is not None and len(finalPubList[i].PMCitedBy) > 0:
            numPM += 1
            gotPM = True
        if gotScholar and gotPM: numBoth += 1
        if gotScholar or gotPM: numEither += 1
    print('Total Entries: ', len(finalPubList))
    print('Number of Scholar Entries: ', numScholar)
    print('Number of PM Entries: ', numPM)
    print('Number of Both: ', numBoth)
    print('Number of either: ', numEither)


def main():
    if constants.GET_CITATIONS:
        getCitation(constants.DATA_FILES, constants.TOPIC+'Labels.pickle', constants.START_INDEX)
    if constants.MERGE_PUBLIST:
        replacePublications(constants.TOPIC+'Labels.pickle')


if __name__ == "__main__":
	main()
