import requests
from scrapy import Selector

for page in range(0,1):
   sapo_url = requests.get(f"https://jobs.dou.ua/vacancies/?exp=0-1")
   selector = Selector(response=sapo_url)

   all_postings = selector.xpath('//div[contains(@class, "content-wrap")]')

   for posting in all_postings:
        title = posting.find_all('.//div[12]/li[2]/a/text()').extract()
        description = posting.find_all('.//div[@class="sh-info"]/text()').extract()
        print(title, description)
