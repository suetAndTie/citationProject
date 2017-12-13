import requests
import xml.etree.ElementTree as ET
import scholarly
import constants

class Publication:
	def __init__(self, title, abstract, date, authors, pmid):
		self.title = title
		self.abstract = abstract
		self.date = date
		self.authors = authors
		self.pmid = pmid
		self.citedBy = set()
		self.PMCitedBy = set()
		self.retrospectiveCitations = []
		self.attemptedRetrieveRetrospectiveCitations = False
		self.attemptedRetrieveCitedBy = False
		self.attemptedPMCitedBy = False
		self.abstractTfidfVector = None
		self.abstractCountVector = None

	def printHi(self):
		print('hey hi hello')

	def genCitedBy(self):
		if self.attemptedRetrieveCitedBy:
			print('Citations for Title already received:', self.title.encode('utf-8'))
			return
		print('Attempting to retrieve citations for Title:', self.title.encode('utf-8'))
		self.attemptedRetrieveCitedBy = True
		query = scholarly.search_pubs_query(self.title)
		paper = next(query, None)
		if paper is None:
			return
		self.citedBy = set(citation.bib['title'] for citation in paper.get_citedby())
		print('Citations retrieved for Title:', self.title.encode('utf-8'))
		print('Cited by list is', str(self.citedBy))
		return self.citedBy

	def genRetrospectiveCitations(self):
		# Only works for articles that are in PMC
		if self.attemptedRetrieveRetrospectiveCitations: return
		self.attemptedRetrieveRetrospectiveCitations = True
		if self.pmid == None:
			return
		try:
			pmreq = requests.get(constants.PM_REQUEST_URL + str(self.pmid))
			if pmreq.status_code != 200:
				return
			pmtree = ET.fromstring(pmreq.text)
			if 'status' in pmtree[1].attrib and pmtree[1].attrib['status'] == 'error':
				return
			else:
				pmcid = pmtree[1].attrib['pmcid']
		except Exception as e:
			print(e)
			return
		pmcreq = requests.get(constants.PMC_REQUEST_URL_PRE + str(pmcid[3:]) + constants.PMC_REQUEST_URL_POST)
		if pmcreq.status_code != 200:
			return
		pmctree = ET.fromstring(pmcreq.text)
		try:
			for child in pmctree[0][2]:
				if child.tag == 'Link':
					self.retrospectiveCitations.append(child[0].text)
		except Exception as e:
			print(e)


	def getCitedByPMCitations(self):
		# Put in PMID and get back PMID of artciles that cite the given article
		if self.attemptedPMCitedBy: return
		self.attemptedPMCitedBy = True
		try:
		    pmreq = requests.get(constants.PM_CITEDBY_URL_PRE + str(self.pmid) + constants.PM_CITEDBY_URL_POST)
		    if pmreq.status_code != 200:
		        return
		    pmtree = ET.fromstring(pmreq.text)
		    for child in pmtree[0][2]:
		        if child.tag == 'Link':
		            self.PMCitedBy.add(child[0].text)
		except Exception as e:
			print(e)


	def pubPrint(self):
		print('Title: %s' % self.title)
		print('Date: %s' % self.date)
		print('Authors: %s' % str(self.authors))
		print('PMID: %s' % self.pmid)
		print('Cited by: %s' % str(self.citedBy))
		print('Retrospective Citations: %s' % str(self.retrospectiveCitations))
		print('PM Cited by: %s' % (str(self.PMCitedBy)))
		print('Abstract: %s' % self.abstract)
		print('Stemmed Abstract: %s' % self.stemmedAbstract)
		print('TfIdf Abstract: %s' % self.abstractTfidfVector)
		print('Count Abstract: %s' % self.abstractCountVector)
