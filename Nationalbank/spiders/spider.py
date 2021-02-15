import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import NationalbankItem

pattern = r'(\r)?(\n)?(\t)?(\xa0)?'

class SpiderSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://www.oenb.at/meldewesen/news.html']

    def parse(self, response):
        articles = response.xpath('//ul[@class="notes press-archive"]/li')
        for article in articles:
            date = article.xpath('.//div[@class="meta"]/span[@class="date"]//text()').get()
            link = article.xpath('.//h2[@class="headline"]/a/@href').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date = date))
        next = response.xpath('//li[@class="lastpage"]/a/@href').get()
        if next:
            yield response.follow(next, self.parse)

    def parse_article(self, response, date):
        item = ItemLoader(NationalbankItem(), response = response)
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        content = [text.strip() for text in response.xpath('//div[@property="description"]//text()').getall() if text.strip()]
        content = re.sub(pattern, "" , ' '.join(content))

        item.add_value('date', date)
        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        return item.load_item()