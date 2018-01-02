#
# Define our Spiders here
# Spiders are classes that Scrapy uses to scrape information from a website
#
# In this file we define spiders that scrape questions asked in Rajya Sabha
#
#

import scrapy
from scrapy.http import FormRequest
from parliamentsearch.items import RajyaSabhaQuestion

from scrapy.selector import Selector


class RSQuestionSpiderSave(scrapy.Spider):
    """
    This spider scrapes the questions asked in Rajya Sabha
    """

    name = "rs_questions_save"
    base_url = 'http://164.100.47.5/qsearch/qsearch.aspx'
    count = 0

    def start_requests(self):
        urls = [
            self.base_url
        ]

        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        """ Scrape list of questions between start and end sessions """
        start_session = 244
        end_session = 244
        view_state = response.css('input#__VIEWSTATE::attr(value)').extract_first()
        event_validation = response.css('input#__EVENTVALIDATION::attr(value)').extract_first()
        formdata = {
            "ctl00$ContentPlaceHolder1$ddlqtype": "ANYTYPE",
            "ctl00$ContentPlaceHolder1$ddlsesfrom": str(start_session),
            "ctl00$ContentPlaceHolder1$ddlsesto": str(end_session),
            "ctl00$ContentPlaceHolder1$btnALL": "AllRec.",
            "__EVENTVALIDATION": event_validation,
            "__VIEWSTATE": view_state
        }
        yield FormRequest(self.base_url, formdata=formdata, callback=self.parse_questions)

    def parse_questions(self, response):
        """ Dumps the response to a file """
        page = response.url.split("/")[-2]
        filename = 'rs-%s.html' % page

        # print("################# {}".format(response.body))

        # q='//div[@id="ctl00_ContentPlaceHolder1_UpdatePanel1"]/table[@id="ctl00_ContentPlaceHolder1_dg"]/tr'
        q='//table[@id="ctl00_ContentPlaceHolder1_dg"]/tr'

        # sel = Selector(response)
        # rows = '//*[@id="ctl00_ContentPlaceHolder1_dg"]/tbody/tr*/td*'

        # sel = Selector(response)
        #
        # rows = sel.xpath(q)
        # print("#####{}".format(rows))
        for tr in response.xpath(q):
            # print('$$$$ {}'.format(tr))
            print(tr.xpath('td/a/text()').extract())

        # print(response.xpath('//title/text()').extract())
       # / print(response.xpath('//table/tr/text()').extract())



        # # rows = response.selector.xpath('//*[@id="ctl00_ContentPlaceHolder1_dg"]/tbody/tr/td/text()').extract()
        #
        # print("%%%%%%%%%%%%%%%%%%%%%%{}".format(rows))
        # for row in rows:
        #     print(row)

        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        #     self.count = self.count + 1
        #     self.log('Saved file %s' % filename)
