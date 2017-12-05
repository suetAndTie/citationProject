# utils
import math
import numpy as np
import scholarly


def l2(x, y):
	dist = 0
	for k, v in x.items():
		if k in y:
			dist += (x[k] - y[k]) ** 2
		else:
			dist += x[k] ** 2
	for k, v in y.items():
		if k not in x:
			dist += y[k] ** 2
	return math.sqrt(dist)

def jaccard(x, y):
	num = 0
	denom = 0
	for k in x:
		if k in y:
			num += 1
		denom += 1
	for k in y:
		if k not in x:
			denom += 1
	if denom is 0:
		return 0
	else:
		return 1. * num / denom

def cosineSimilarity(x, y):
	num = 0
	for k, v in x.items():
		if k in y:
			num += x[k] * y[k]
	denom = l2(x, {}) * l2(y, {})
	return 1. * num / denom

# takes in two dates of yyyy mmm format where mmm is a string
def dateDifference(x, y):
	if x is None or y is None:
		return 0
	monthMap = {
		"Jan": 1,
		"Feb": 2,
		"Mar": 3,
		"Apr": 4,
		"May": 5,
		"Jun": 6,
		"Jul": 7,
		"Aug": 8,
		"Sep": 9,
		"Oct": 10,
		"Nov": 11,
		"Dec": 12
	}
	# print(x)
	# print(y)
	year1 = int(x[:4])
	year2 = int(y[:4])
	# If no month, return difference in year
	if len(x) == 4 or len(y) == 4: return abs((12 * year1) - (12 * year2))
	month1 = monthMap[x[5:]]
	month2 = monthMap[y[5:]]
	return abs((12 * year1 + month1) - (12 * year2 + month2))


# Features defined as:
# [L2 distance, Jaccard Distance, Cosine distance (of abstract vectors),
# l2 * j, l2 * c, j * c, l2 * j * c,
# num shared retrospective citations,
# num shared authors,
# abs(distance between pub dates),
# squared diff between smallest three eigenvectors of laplacian graph]

# somehow need to figure out how to pass in laplacian matrix
# each element of feature vector should increase if probability that papers are related increases
def extractFeatures(
		abstract1,
		abstract2,
		authors1,
		authors2,
		retrospectiveCitations1,
		retrospectiveCitations2,
		pubDateDiff, #diff in months
		laplacianMatrix = None):
	l2Dist = l2(abstract1, abstract2)
	jDist = jaccard(abstract1, abstract2)
	cDist = cosineSimilarity(abstract1, abstract2)
	numSharedAuthors = jaccard(authors1, authors2)
	numSharedCitations = jaccard(retrospectiveCitations1, retrospectiveCitations2)
	features = [
		1. / l2Dist if l2Dist != 0 else 0,
		jDist,
		cDist,
		1. * jDist / l2Dist if l2Dist != 0 else 0,
		1. * cDist / l2Dist if l2Dist != 0 else 0,
		1. * jDist * cDist,
		1. / l2Dist * jDist * cDist if l2Dist != 0 else 0,
		numSharedAuthors,
		numSharedCitations,
		1. / pubDateDiff if pubDateDiff != 0 else 0
	]
	if laplacianMatrix is not None:
		# w, v = np.linalg.eig(laplacianMatrix)
		# indices = np.argsort(w)
		# values = []
		a = 0 # dummy varaiable until i figure out what to put here
	return features

def getCitations(x):
	xQuery = scholarly.search_pubs_query(x)
	xPaper = next(xQuery, None)
	if xPaper is None:
		return None
	return set(citation.bib['title'] for citation in xPaper.get_citedby())

def areCoCited(x, y):
	for paper in x:
		if paper in y:
			return True
	return False
