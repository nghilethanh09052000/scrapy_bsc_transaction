import scrapy
import json
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
import datetime
from urllib.parse import quote
from selenium.common.exceptions import NoSuchElementException
import logging
from scrapy.exceptions import CloseSpider

class IndexSpider(scrapy.Spider):

    name = "index"
    headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'Referer': f'https://bscscan.com/token/0x31e4efe290973ebe91b3a875a7994f650942d28f',
                'Sec-Fetch-Dest': 'iframe',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Upgrade-Insecure-Requests': '1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, utf-8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
            }
    cookies =  {
        "ASP.NET_SessionId": "mapjhh2cox4s4qir1hkowqdx",
        "_ga": "GA1.1.317281229.1702446795",
        "bscscan_offset_datetime": "+7",
        "__stripe_mid": "947e6c1a-e177-48f2-a5c9-b3cfd5c53f20e41efd",
        "bscscan_pwd": "4792:Qdxb:ZVSnvz6nUbfuSyaEdr/DTA6gHjtomNgzD6/4Dy6Tzx3qPGwBmDaOvqos7NKaCUNN",
        "bscscan_userid": "nghilethanh",
        "bscscan_autologin": "True",
        "__cuid": "8b6ec33faf5e4941b3462dea5967778d",
        "amp_fef1e8": "e1af751e-aa10-49ec-b2e2-e003b38c5060R...1hhjue9nv.1hhjuemsm.3.1.4",
        "__cflb": "0H28vyb6xVveKGjdV3CYUMgiti5JgVrVnyTmxiunQzx",
        "cf_chl_2": "93cc633eb00a6f2",
        "cf_clearance": "mnWgVtJaxKqZyBPaZkUZHh64QI5jtWhGGuoelplBQq0-1702624121-0-1-1ec25fd0.9dc3df80.bcf4d68a-150.2.1702624121",
        "_ga_PQY6J2Q8EP": "GS1.1.1702624108.12.1.1702624210.0.0.0"
        }

    page = 1
    last_page = None

    def start_requests(self):
        token_address = self.token_address
        yield scrapy.Request(
            url      = f"https://bscscan.com/token/generic-tokentxns2?m=light&contractAddress={token_address}&a=&sid=0cb6f9a2531e772f1e77d4fddc2b23d0&p=1",
            callback  = self.get_page,
            headers= self.headers,
            cookies = self.cookies,
            dont_filter=True  
        )

    def get_page(self, response, **kwargs):
        

        if not self.last_page:
            self.last_page = response.xpath('//nav[@aria-label="page navigation"]/ul/li[last()]/a/@href').get().split('&p=')[1].replace("')","")

        yield scrapy.Request(
            url      = f"https://bscscan.com/token/generic-tokentxns2?m=light&contractAddress={self.token_address}&a=&sid=0cb6f9a2531e772f1e77d4fddc2b23d0&p={self.page}",
            callback  = self.parse,
            headers= self.headers,
            cookies = self.cookies,
            meta= {
                'page': self.page
            },
            dont_filter=True  
        )
            
    def parse(self, response, **kwargs):
      
        page = response.meta['page']

        tr_elements = response.xpath('//table/tbody/tr')
        if not tr_elements:
            logging.info(f"Can not find elements in this page, Calling Again To Get Data---------------", page)
            return

        for tr_element in tr_elements:

            age = tr_element.xpath("./td[@class='showAge ']/span/text()").get()
            
            if 'day' in age:
                day = age.split('day')[0]
                if int(day) >= 1: 
                    return
            
            yield {
                'token_address' : self.token_address,
                'txn_hash'      : tr_element.xpath("./td/span/a/text()").get(),
                'method'        : tr_element.xpath("./td/span[@data-bs-boundary='viewport']/text()").get(),
                'age'           : age,
                'from_address'  : tr_element.xpath("./td[7]/div/a[@class='js-clipboard link-secondary ']/@data-clipboard-text").get(),
                'to_address'    : tr_element.xpath("./td[9]/div/a[@class='js-clipboard link-secondary ']/@data-clipboard-text").get(),
                'quantity'      : tr_element.xpath("./td[10]/text()").get().replace(',', ''),
            }

        self.page += 1
        if self.page <= int(self.last_page):
            yield scrapy.Request(
                url      = f"https://bscscan.com/token/generic-tokentxns2?m=light&contractAddress={self.token_address}&a=&sid=0cb6f9a2531e772f1e77d4fddc2b23d0&p={self.page}",
                callback  = self.parse,
                headers= self.headers,
                cookies = self.cookies,
                meta= {
                    'page': self.page
                },
                dont_filter=True  
            )
