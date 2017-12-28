#
# Define our Spiders here
# Spiders are classes that Scrapy uses to scrape information from a website
#
#

import scrapy
from parliamentsearch.items import MemberofParliament


class MPListSpider(scrapy.Spider):
    """
    This spider scrapes the list of MPs
    """

    name = "list_of_mps"

    def start_requests(self):
        urls = [
            'http://164.100.47.194/Loksabha/Members/AlphabeticalList.aspx'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse);

    def parse(self, response):
        mp_list = response.xpath('//table[@id="ContentPlaceHolder1_tblMember"]//tr//tr[@class="odd"]')
        print('Total number of MPs:', len(mp_list))
        for mp in mp_list:
            entry = mp.xpath('.//text()').extract()

            mp = MemberofParliament();
            mp['mp_id'] = entry[1].strip();
            mp['mp_name'] = entry[6].strip();
            mp['mp_party'] = entry[9].strip();
            mp['mp_constituency'] = entry[11].strip();
            print(mp['mp_id'], '\t', mp['mp_name'], '\t', mp['mp_party'], '\t', mp['mp_constituency'])


class MPListSpiderSave(scrapy.Spider):
    """
    This spider scrapes the list of MPs and saves the html to a file
    This is mainly useful for debug
    """

    name = "list_of_mps_save"

    def start_requests(self):
        urls = [
            'http://164.100.47.194/Loksabha/Members/AlphabeticalList.aspx'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse);

    def parse(self, response):
        mp_list = response.xpath('//table[@id="ContentPlaceHolder1_tblMember"]//tr//tr[@class="odd"]')
        print('Total number of MPs:', len(mp_list))

        # save the content to a file - only for debug
        page = response.url.split("/")[-2]
        filename = 'list-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
            self.log('Saved file %s' % filename)
