import scrapy
from scrapy import Request

class ZameenSpider(scrapy.Spider):
    name = "spider"
    start_urls = [
        'https://www.zameen.com/all-cities/pakistan-1-9.html'
    ]

    custom_settings = {
        "FEED_FORMAT": 'json',
        "FEED_URI": 'results.json'
    }

    def parse(self, response):
        cities_names = response.xpath('//li[@class="_45afd756"]/a/text()').extract()
        cities_urls = response.xpath('//li[@class="_45afd756"]/a/@href').extract()

        for name, url in zip(cities_names, cities_urls):
            meta = {
                'city_name': name,
                'city_url': url
            }
            yield Request(response.urljoin(url), self.parse_inside_city, meta=meta)

    def parse_inside_city(self, response):
        location_names = response.xpath('//div[@class="_5922efef"]/ul/li/a/text()').extract()
        location_urls = response.xpath('//div[@class="_5922efef"]/ul/li/a/@href').extract()

        for name, url in zip(location_names, location_urls):
            meta = {
                'city_name': response.meta['city_name'],
                'city_url': response.meta['city_url'],
                'location_name': name,
                'location_url': url
            }
            yield Request(response.urljoin(url), self.parse_inside_location, meta=meta)

    def parse_inside_location(self, response):

        # print(response.url)

        for li in response.xpath('//li[@aria-label="Listing"]'):
            price = li.xpath('//span[@aria-label="Price"]/text()').get()
            title = li.xpath('//h2[@aria-label="Title"]/text()').get()
            beds = li.xpath('//span[@aria-label="Beds"]/text()').get()
            baths = li.xpath('//span[@aria-label="Baths"]/text()').get()
            area = li.xpath('//div[@class="_1e0ca152 _026d7bff"]/div/span/text()').get()
            image = li.xpath('//img[@aria-label="Listing photo"]/@data-src').get()
            url = response.urljoin(li.xpath('//a[@class="_7ac32433"]/@href').get())

            yield {
                'city_name': response.meta['city_name'],
                'city_url': response.meta['city_url'],
                'location_name': response.meta['location_name'],
                'location_url': response.meta['location_url'],
                'price': price,
                'title': title,
                'beds': beds,
                'baths': baths,
                'area': area,
                'image': image,
                'url': url
            }

        next_page = response.xpath('//a[@title="Next"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_inside_location)


