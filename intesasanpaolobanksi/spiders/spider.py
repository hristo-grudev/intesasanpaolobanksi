import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import IntesasanpaolobanksiItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.intesasanpaolobank.si/aboutUsSectionServlet/?operation=getPressNewsList"

payload="{\"component\":\"4e1b9fae-3fd9-428e-89c3-7d2e91c9142d\",\"bankName\":\"ISPSLOVENIA\",\"numberLastYears\":\"120\",\"language\":\"\"}"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
  'Accept': 'application/json, text/plain, */*',
  'contextPath': '',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
  'Content-Type': 'application/json',
  'Origin': 'https://www.intesasanpaolobank.si',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.intesasanpaolobank.si/prebivalstvo/o-banki/novosti-in-publikacije/aktualne-objave.html',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': '_ga=GA1.2.1650019283.1615378693; _gid=GA1.2.1141760631.1615378693; _cs_c=1; _CT_RS_=Recording; WRUID=3199931101020216; _cs_cvars=%7B%221%22%3A%5B%22Page%20Type%22%2C%22aboutUsSectionPage%22%5D%2C%222%22%3A%5B%22Page%20Name%22%2C%22ISPSLOVENIA%3ARetail%3AAbout%20Us%3ANews%20And%20Publications%3APress%20And%20News%22%5D%2C%223%22%3A%5B%22Intesa%20Bank%22%2C%22ISPSLOVENIA%22%5D%2C%224%22%3A%5B%22Site%20Language%20%22%2C%22Sl%22%5D%2C%225%22%3A%5B%22Site%20Country%22%2C%22Slovenia%22%5D%2C%226%22%3A%5B%22Portal%20Section%22%2C%22public%22%5D%2C%227%22%3A%5B%22Visitor%20Type%22%2C%22guest%22%5D%2C%228%22%3A%5B%22Customer%20Segment%22%2C%22Retail%22%5D%7D; _gat_UA-129304750-5=1; JSESSIONID=bv4u_BdLczKDYJjFrp2GcLCbc-QV9JybjG7HCqqS; _cs_id=ff40b40a-8f0f-aef9-c479-c184c9bf56a4.1615378694.2.1615449222.1615449115.1.1649542694468.Lax.0; _cs_s=3.1; __CT_Data=gpv=6&ckp=tld&dm=intesasanpaolobank.si&apv_61_www56=6&cpv_61_www56=6&rpv_61_www56=6; JSESSIONID=bv4u_BdLczKDYJjFrp2GcLCbc-QV9JybjG7HCqqS'
}


class IntesasanpaolobanksiSpider(scrapy.Spider):
	name = 'intesasanpaolobanksi'
	start_urls = ['https://www.intesasanpaolobank.si/prebivalstvo/o-banki/novosti-in-publikacije/aktualne-objave.html']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = json.loads(data.text)
		for el in raw_data:
			title = el["title"]
			date = el["date"]
			descr = el["description"]
			link = el["readMoreLink"]
			if not link:
				yield response.follow(response.url, self.parse_instant, dont_filter=True, cb_kwargs={'title': title, 'date': date, 'descr': descr})
			yield response.follow(link, self.parse_post, cb_kwargs={'title': title, 'date': date})

	def parse_instant(self, response, title, date, descr):
		item = ItemLoader(item=IntesasanpaolobanksiItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', descr)
		item.add_value('date', date)

		return item.load_item()

	def parse_post(self, response, title, date):
		description = response.xpath('//div[@class="cmsTextWrpper section__contentWrapper"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=IntesasanpaolobanksiItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
