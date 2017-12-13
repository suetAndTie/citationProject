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
    if listStartIndex + constants.NUM_PAPERS_CITATION >= len(publicationList):
        listEndIndex = len(publicationList)
    else:
        listEndIndex = listStartIndex + constants.NUM_PAPERS_CITATION
    currList = publicationList[listStartIndex:listEndIndex]
    for i in xrange(len(currList)):
        currList[i].genRetrospectiveCitations()
        currList[i].getCitedByPMCitations()
    with concurrent.futures.ThreadPoolExecutor(max_workers = constants.MAX_WORKERS) as executor:
        future_to_article = {executor.submit(currList[i].genCitedBy): currList[i].title for i in xrange(len(currList))}
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


# After running getCitation for all of the publications, this function will replace
# the original publist with the new entries
# Puts the final pubList into finalpubList file
def replacePublications(labelOutputFile):
    finalPubList = []
    for startIndex in constants.START_INDEX_LIST:
        with open(str(startIndex) + 'temp' + labelOutputFile, 'rb') as f:
    		currPubList = pickle.load(f)
        endIndex = startIndex + len(currPubList)
        finalPubList[startIndex:endIndex] = currPubList
    with open('temp' + labelOutputFile, 'wb') as f:
        pickle.dump(finalPubList, f)

    numGood = 0
    for i in xrange(len(finalPubList)):
        if finalPubList[i].citedBy is not None and len(finalPubList[i].citedBy) > 0:
            numGood += 1
    print 'Total Entries: ', len(finalPubList)
    print 'Number of Good Entries: ', numGood


def main():
    if constants.GET_CITATIONS:
        getCitation(constants.DATA_FILES, constants.TOPIC+'Labels.pickle', constants.START_INDEX_LIST[constants.START_INDEX])
    if constants.MERGE_PUBLIST:
        replacePublications(constants.TOPIC+'Labels.pickle')


if __name__ == "__main__":
	main()
