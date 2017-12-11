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
		self.retrospectiveCitations = []
		self.attemptedRetrieveRetrospectiveCitations = False
		self.attemptedRetrieveCitedBy = False
		self.abstractTfidfVector = None
		self.abstractCountVector = None

	def printHi(self):
		print('hey hi hello')

	def genCitedBy(self):
		if self.attemptedRetrieveCitedBy:
			print('Citations for Title: %s already retrieved' % self.title)
			return
		print('Attempting to retrieve citations for Title: %s' % self.title)
		self.attemptedRetrieveCitedBy = True
		query = scholarly.search_pubs_query(self.title)
		paper = next(query, None)
		if paper is None:
			return
		self.citedBy = set(citation.bib['title'] for citation in paper.get_citedby())
		print('Citations retrieved for Title: %s\n Cited by list is %s' % (self.title, str(self.citedBy)))
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

	def pubPrint(self):
		print('Title: %s' % self.title)
		print('Date: %s' % self.date)
		print('Authors: %s' % str(self.authors))
		print('PMID: %s' % self.pmid)
		print('Cited by: %s' % str(self.citedBy))
		print('Retrospective Citations: %s' % str(self.retrospectiveCitations))
		print('Abstract: %s' % self.abstract)
		print('Stemmed Abstract: %s' % self.stemmedAbstract)
		print('TfIdf Abstract: %s' % self.abstractTfidfVector)
		print('Count Abstract: %s' % self.abstractCountVector)
