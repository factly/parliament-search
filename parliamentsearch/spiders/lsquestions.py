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
from parliamentsearch.items import LokSabhaQuestion



class LSQuestionSpider(scrapy.Spider):
	"""
	This spider scrapes the questions asked in Lok Sabha
	"""

	name = "ls_questions"
	active_sessions = [16, 15, 14, 13, 12]  # most recent at the beginning
	base_url = 'http://164.100.47.194/Loksabha/Questions/qsearch15.aspx?lsno='

	def start_requests(self):
		# extract only from current active session at the moment
		base_urls = [self.base_url + str(s) for s in self.active_sessions[:1]]
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
				page_url = self.base_url + str(current_session)
				formdata["ctl00$ContentPlaceHolder1$txtpage"] = str(n)

				callback = lambda response: self.parse_questions(response, current_session)
				yield FormRequest.from_response(response, formdata=formdata, callback=callback)

	def parse_questions(self, response, current_session):
		sel = Selector(response)
		q_table_rows = sel.xpath('//div[@id="ContentPlaceHolder1_pnlDiv"]/table[@id="ContentPlaceHolder1_tblMember"]/tr/td/table[@class="member_list_table"]/tr')
		for i, tr in enumerate(q_table_rows):
			qtn = LokSabhaQuestion()

			row = tr.xpath('td/a/text()').extract()
			qtn['q_session'] = current_session
			qtn['q_no'] = int(row[0])
			qtn['q_type'] = row[1].strip().lower()
			eng_url = ''
			hindi_url = ''
			if qtn['q_type'] == 'starred':
				eng_url = tr.xpath('td[2]/a[5]/@href').extract()[0]
				hindi_url = tr.xpath('td[2]/a[7]/@href').extract()[0]
			qtn['q_date'] = row[4]
			qtn['q_ministry'] = row[5]
			qtn['q_member'] = row[6]
			qtn['q_subject'] = row[7]

			print(qtn)
			if qtn['q_type'] == 'starred':
				print(eng_url)
				print(hindi_url)


	def save_response(self, response):
		""" Dumps the response to a file - useful for debug """
		page = response.url.split("/")[-2]
		filename = 'ls-%s.html' % page
		with open(filename, 'wb') as f:
			f.write(response.body)
			self.log('Saved file %s' % filename)
