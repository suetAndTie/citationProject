# Data generation.py

import PubmedStringParser
import os.path
import pickle
import concurrent.futures
import Publication
import constants
import util
import numpy as np

def generateDataAndLabels(inputFiles, matrixOutputFile, controlMatrixOutputFile, labelOutputFile, dateRange = None):
	if os.path.isfile(matrixOutputFile) and os.path.isfile(controlMatrixOutputFile) and os.path.isfile(labelOutputFile):
		print('Opening old file')
		with open(matrixOutputFile, 'rb') as f:
			pubRelations = pickle.load(f)
		with open(controlMatrixOutputFile, 'rb') as f:
			controlPubRelations = pickle.load(f)
		with open(labelOutputFile, 'rb') as f:
			labels = pickle.load(f)
			return pubRelations, controlPubRelations, labels
	if os.path.isfile('temp' + labelOutputFile):
		with open('temp' + labelOutputFile, 'rb') as f:
			publicationList = pickle.load(f)
	else:
		publicationList = PubmedStringParser.getAllData(inputFiles)
		for i in range(len(publicationList)):
			publicationList[i].genRetrospectiveCitations()
			publicationList[i].getCitedByPMCitations()
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
		with open('temp' + labelOutputFile, 'wb') as f:
			pickle.dump(publicationList, f)
	# for publication in publicationList:
	# 	publication.pubPrint()
	# Experimental vs control publication relations (eg TF-IDF vs count)
	publicationRelationships = []
	controlPubRelations = []
	labels = []
	for i in range(len(publicationList)):
		if len(publicationList[i].abstract) == 0: continue
		# if len(publicationList[i].citedBy) == 0: continue
		for j in range(i + 1, len(publicationList)):
			if len(publicationList[j].abstract) == 0: continue
			# if len(publicationList[j].citedBy) == 0: continue
			if dateRange == None or util.dateDifference(publicationList[i].date, publicationList[j].date) <= dateRange:
				publicationRelationships.append(util.extractFeatures(publicationList[i], publicationList[j], 'tfidf'))
				controlPubRelations.append(util.extractFeatures(publicationList[i], publicationList[j], 'count'))
				citedByI = publicationList[i].citedBy
				citedByJ = publicationList[j].citedBy
				pmCitedByI = publicationList[i].PMCitedBy
				pmCitedByJ = publicationList[j].PMCitedBy
				if len(citedByI & citedByJ) == 0 and len(pmCitedByI & pmCitedByJ) == 0:
					labels.append(0)
				else:
					labels.append(1)
	# Convert to np array
	publicationRelationships = np.array(publicationRelationships)
	controlPubRelations = np.array(controlPubRelations)
	labels = np.array(labels)
	print('Saving new file')
	with open(matrixOutputFile, 'wb') as f:
		pickle.dump(publicationRelationships, f)
	with open(controlMatrixOutputFile, 'wb') as f:
		pickle.dump(controlPubRelations, f)
	with open(labelOutputFile, 'wb') as f:
		pickle.dump(labels, f)
	return publicationRelationships, controlPubRelations, labels
