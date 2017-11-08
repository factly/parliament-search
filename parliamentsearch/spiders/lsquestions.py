#
# Define our Spiders here
# Spiders are classes that Scrapy uses to scrape information from a website
#
# In this file we define spiders that scrape questions in Lok Sabha
#
#

import scrapy
from scrapy.selector import Selector
from scrapy.http import FormRequest
from urllib.parse import urlencode
from parliamentsearch.items import LokSabhaQuestion, LSQnFields



class LSQuestionSpider(scrapy.Spider):
	"""
	This spider scrapes the questions asked in Lok Sabha
	"""

	name = "ls_questions"
	active_sessions = [16, 15, 14, 13, 12]  # most recent at the beginning
	base_url = 'http://164.100.47.194/Loksabha/Questions/qsearch15.aspx'

	def start_requests(self):
		# extract only from current active session at the moment
		base_urls = [self.base_url + '?' + urlencode({'lsno': s}) \
					 for s in self.active_sessions[:1]]
		for url in base_urls:
			yield scrapy.Request(url, callback=self.parse)

	def parse(self, response):
		""" Scrape list of questions of all sessions """

		sel = Selector(response)
		fields = ["ContentPlaceHolder1_ddlfrom", \
				  "ContentPlaceHolder1_ddlto", \
				  "ContentPlaceHolder1_ddlsesfrom", \
				  "ContentPlaceHolder1_ddlsesto"]
		selected_options = []
		for field in fields:
			query = '//select[@id="{0}"]/option[@selected="selected"]/@value'.format(field)
			selected_options.append(sel.xpath(query).extract()[0])
		print(selected_options)

		"""
		FormRequest.from_response() below will use values from the form unless
		overridden explicitly so update only required values
		"""
		formdata = {
			"ctl00$ContentPlaceHolder1$btngo": "Go",
			"ctl00$ContentPlaceHolder1$ddlqtype" : "ANYTYPE",
			"ctl00$ContentPlaceHolder1$sort": "btndate",
			"ctl00$ContentPlaceHolder1$ddlfrom": selected_options[0],
			"ctl00$ContentPlaceHolder1$ddlto": selected_options[1],
			"ctl00$ContentPlaceHolder1$ddlsesfrom": selected_options[2],
			"ctl00$ContentPlaceHolder1$ddlsesfrom": selected_options[3],
			"__EVENTVALIDATION": sel.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
			"__VIEWSTATE": sel.css('input#__VIEWSTATE::attr(value)').extract_first(),
			"__VIEWSTATEGENERATOR": sel.css('input#__VIEWSTATEGENERATOR::attr(value)').extract_first()
		}

		"""
		Extract the current session from the selected value in drop down list. This
		can also be extracted from url string but this is preferred
		"""
		session = sel.xpath('//select[@id="ContentPlaceHolder1_ddlls"]')
		current_session = int(session.xpath('option[@selected="selected"]/@value').extract()[0])
		print('Current Session:', current_session)

		num_pages_span = sel.xpath('//div[@id="ContentPlaceHolder1_pagingpanel"]/table/tr/td')
		num_pages_text = num_pages_span.xpath('span[@id="ContentPlaceHolder1_lblfrom"]/text()').extract()[0]
		num_pages = int(num_pages_text.split()[1])
		print('No. of pages:', num_pages)


		# loop through pages and scrape all questions
		if num_pages:
			# for now try to scrape data only from 2 pages
			for n in range(1, 3):
				page_url = self.base_url + '?' + urlencode({'lsno': current_session})
				formdata["ctl00$ContentPlaceHolder1$txtpage"] = str(n)

				callback = lambda response: self.parse_questions(response, current_session)
				yield FormRequest.from_response(response, formdata=formdata, callback=callback)

	def parse_questions(self, response, current_session):
		"""This is the response for a set of questions (10) of the given session. This
		is usually called repeatedly as per number of pages to parse all
		questions
		"""
		sel = Selector(response)

		q_table_rows = sel.xpath('//div[@id="ContentPlaceHolder1_pnlDiv"]/table[@id="ContentPlaceHolder1_tblMember"]/tr/td/table[@class="member_list_table"]/tr')

		# list of questions available in a page
		# all of these are inserted into db at once
		questions = []
		for i, tr in enumerate(q_table_rows):
			row = []
			urls = None
			for j, td in enumerate(tr.xpath('td')):
				field = td.xpath('a/text()').extract()
				row.append(field)

				if field[0].strip().lower() == 'starred':
					urls = td.xpath('a/@href').extract()

			row.append(urls)
			q = self.parse_items(current_session, row)
			questions.append(q)

		yield {'questions': questions }


	def parse_items(self, session, row):
		"""
		row is a list which contains values of all fields for a particular
		question. In this function we create item object and populate them with
		required fields
		"""

		q = LokSabhaQuestion()

		q['q_session'] = session
		q['q_no'] = int(row[LSQnFields.NUM.value][0])
		q['q_type'] = row[LSQnFields.TYPE.value][0].strip().lower()
		q['q_annex'] = {}
		if q['q_type'] == 'starred':
			for u, val in enumerate(row[LSQnFields.ANNEX.value][1:]):
				annex_name = row[LSQnFields.TYPE.value][u+1]
				# TODO: this is not consistent in all sessions so restrict for now
				if annex_name == 'PDF/WORD' or \
				   annex_name == 'PDF/WORD(Hindi)' or \
				   annex_name == 'Annexure':
					q['q_annex'][row[LSQnFields.TYPE.value][u+1]] = val

		q['q_date'] = row[LSQnFields.DATE.value][0]
		q['q_ministry'] = row[LSQnFields.MINISTRY.value][0]
		q['q_member'] = row[LSQnFields.MEMBERS.value]
		q['q_subject'] = row[LSQnFields.SUBJECT.value][0]
		params = row[LSQnFields.ANNEX.value][0].split('?')[1]
		q['q_url'] = self.base_url + '?' + params

		return q

	def save_response(self, response):
		""" Dumps the response to a file - useful for debug """
		page = response.url.split("/")[-2]
		filename = 'ls-%s.html' % page
		with open(filename, 'wb') as f:
			f.write(response.body)
			self.log('Saved file %s' % filename)
