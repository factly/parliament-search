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
from newspaper import Article
from newspaper import fulltext
import urllib

from urllib.parse import parse_qsl

from ..models import PQDataModel
from datetime import datetime


class LSQuestionSpider(scrapy.Spider):
    """
    This spider scrapes the questions asked in Lok Sabha
    """

    name = "ls_questions"
    # active_sessions = [16, 15, 14, 13, 12]  # most recent at the beginning
    # active_sessions = [15, 14, 13, 12]  # most recent at the beginning
    active_sessions = [12]  # most recent at the beginning
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

        print("SELECTED options \n {}".format(selected_options))

        """
        FormRequest.from_response() below will use values from the form unless
        overridden explicitly so update only required values
        """
        formdata = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": sel.css('input#__VIEWSTATE::attr(value)').extract_first(),
            "__VIEWSTATEGENERATOR": sel.css('input#__VIEWSTATEGENERATOR::attr(value)').extract_first(),
            "__VIEWSTATEENCRYPTED": "",
            "__EVENTVALIDATION": sel.css('input#__EVENTVALIDATION::attr(value)').extract_first(),
            "ctl00$txtSearchGlobal":"",
            "ctl00$ContentPlaceHolder1$ddlfile":".pdf",
            "ctl00$ContentPlaceHolder1$TextBox1": "",
            "ctl00$ContentPlaceHolder1$btn": "allwordbtn",
            "ctl00$ContentPlaceHolder1$btn1": "titlebtn",
            "ctl00$ContentPlaceHolder1$ddlmember": "--- Select Member Name ---",
            "ctl00$ContentPlaceHolder1$ddlministry": "--- Select Ministry Name ---",
            "ctl00$ContentPlaceHolder1$ddlfrom": selected_options[0],
            "ctl00$ContentPlaceHolder1$ddlto": selected_options[1],
            "ctl00$ContentPlaceHolder1$ddlqtype": "ANYTYPE",
            "ctl00$ContentPlaceHolder1$ddlsesfrom": selected_options[2],
            "ctl00$ContentPlaceHolder1$ddlsesto": selected_options[3],
            "ctl00$ContentPlaceHolder1$txtqno": "",
            "ctl00$ContentPlaceHolder1$sort": "btndate",
            "ctl00$ContentPlaceHolder1$txtpage": 1,
            "ctl00$ContentPlaceHolder1$btngo": "Go"
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
            for n in range(499, 501):
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

        q_table_rows = sel.xpath(
            '//div[@id="ContentPlaceHolder1_pnlDiv"]/table[@id="ContentPlaceHolder1_tblMember"]/tr/td/table[@class="member_list_table"]/tr')

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

                if field[0].strip().lower() == 'unstarred':
                    urls = td.xpath('a/@href').extract()

            row.append(urls)
            q = self.parse_items(current_session, row, response)
            questions.append(q)

        yield {'questions': questions}

    def parse_items(self, session, row, response):
        """
        row is a list which contains values of all fields for a particular
        question. In this function we create item object and populate them with
        required fields
        """
        self.log('###################### \n {}'.format(row))

        q = dict()

        q['question_origin'] = 'loksabha'
        q['question_number'] = int(row[LSQnFields.NUM.value][0])
        q['question_type'] = row[LSQnFields.TYPE.value][0].strip().lower()
        q['question_session'] = session

        q['question_date'] = row[LSQnFields.DATE.value][0]
        q['question_ministry'] = row[LSQnFields.MINISTRY.value][0]
        q['question_member'] = row[LSQnFields.MEMBERS.value]
        q['question_subject'] = row[LSQnFields.SUBJECT.value][0]

        q_row = row[LSQnFields.ANNEX.value]
        q['question_annex'] = {}
        if q['question_type'] in ['starred', 'unstarred'] and isinstance(q_row, list):
            for u, val in enumerate(q_row[1:]):
                annex_name = row[LSQnFields.TYPE.value][u + 1]
                # TODO: this is not consistent in all sessions so restrict for now
                if annex_name in ['PDF/WORD' , 'PDF/WORD(Hindi)', 'Annexure']:
                    q['question_annex'][row[LSQnFields.TYPE.value][u + 1]] = val

        if isinstance(q_row, list):
            first_url = q_row[0]
            url_list = self.base_url.split('/')[0:-1]
            url_list.append(first_url)
            url = "/".join(url_list)
            q['question_url'] = url
            q['question_text'] = self.get_text(url)
            qref = dict(parse_qsl(first_url))['QResult15.aspx?qref']
            q['question_number'] = str(session) + str(qref)

        self.insert_in_db(q)

        return q

    def save_response(self, response):
        """ Dumps the response to a file - useful for debug """
        page = response.url.split("/")[-2]
        filename = 'ls-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
            self.log('Saved file %s' % filename)

    def get_text(self, url):
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as ex:
            self.log('Failed to extract Text information'.format(ex))

    def insert_in_db(self, q):
        record = PQDataModel()
        record.question_number = q['question_number']
        record.question_origin = q['question_origin']
        record.question_type = q['question_type']
        record.question_session = q['question_session']
        record.question_ministry = q['question_ministry']
        record.question_member = q['question_member']
        record.question_subject = q['question_subject']
        record.question_type = q['question_type']
        record.question_annex = q['question_annex']
        record.question_url = q['question_url']
        record.question_text = q['question_text']
        record.question_url = q['question_url']
        record.question_date = datetime.strptime(q['question_date'], '%d.%m.%Y')
        record.save()



