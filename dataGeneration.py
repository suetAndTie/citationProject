# Data generation.py

import PubmedStringParser
import os.path
import pickle
import concurrent.futures
import Publication
import constants
import util

def generateDataAndLabels(inputFiles, outputFile, dateRange = None):
	if os.path.isfile(outputFile):
		print('Opening old file')
		with open(outputFile, 'rb') as f:
			publicationRelationships, labels = pickle.load(f)
			return publicationRelationships, labels
	publicationList = PubmedStringParser.getAllData(inputFiles)
	for i in range(len(publicationList)):
		publicationList[i].genRetrospectiveCitations()
	with concurrent.futures.ThreadPoolExecutor(max_workers = constants.MAX_WORKERS) as executor:
		future_to_article = {executor.submit(publicationList[i].genCitedBy): publicationList[i].title for i in range(len(publicationList))}
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
	with open('temp' + outputFile, 'wb') as f:
		pickle.dump(publicationList, f)
	for publication in publicationList:
		publication.print()
	publicationRelationships = []
	labels = []
	for i in range(len(publicationList)):
		for j in range(i + 1, len(publicationList)):
			if dateRange == None or util.dateDifference(publicationList[i].date, publicationList[j].date) <= dateRange:
				publicationRelationships.append(util.extractFeatures(publicationList[i], publicationList[j]))
				citedByI = publicationList[i].citedBy
				citedByJ = publicationList[j].citedBy
				if len(citedByI & citedByJ) == 0:
					labels.append(0)
				else:
					labels.append(1)
	with open(outputFile, 'wb') as f:
		print('Saving new file')
		pickle.dump((publicationRelationships, labels), f)
	return publicationRelationships, labels