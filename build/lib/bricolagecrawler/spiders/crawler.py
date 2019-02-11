# -*- coding: utf-8 -*-
import scrapy
from bricolagecrawler.items import MrbricolagecrawlerItem


class CrawlerSpider(scrapy.Spider):
    name = 'crawler'
    allowed_domains = ['mr-bricolage.bg']
    start_urls = ['https://mr-bricolage.bg/bg/Каталог/Инструменти/Авто-и-велоаксесоари/Велоаксесоари/c/006008012']

    def parse(self, response):
        for product in response.css('.product-item'):
            links = product.css('.product > .title > a.name::attr("href")').extract()
            if len(links) > 0:
                for product_link in links:
                    url = 'https://mr-bricolage.bg' + product_link
                    yield scrapy.Request(url, callback=self.parse_get_more_details)
                    
        for next_page in response.css('li.pagination-next a::attr("href")'):
            yield response.follow(next_page, self.parse)

    def parse_get_more_details(self, response):
        product = MrbricolagecrawlerItem()
        response = response.css('body > main > div:nth-child(4) > section > div > div.row')
        price = response.css('div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div > p::text').extract_first().strip()
        price_without_currency = float(price.split()[0].replace(",", "."))

        # Primary product information
        product['title'] = response.css('div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > h1::text').extract_first().strip()
        product['price'] = price
        product['price_without_currency'] = format(price_without_currency, ".2f")
        product['image'] = "https://mr-bricolage.bg" + str(response.xpath('//html/body/main/div[4]/section/div/div[2]/div[1]/div[2]/div/img/@src').extract_first())
        # END of Primary product information

        # Product specifications
        ean_title = response.xpath('//*[@id="home"]/div[1]/span/strong/text()').extract_first().strip()
        ean_title = ean_title.replace(" ", "_")
        ean_number = response.xpath('//*[@id="home"]/div[1]/span/text()').extract()[1].strip()

        ean = {}
        ean[ean_title] = ean_number

        products_specifications = []
        products_specifications.append(ean)

        is_specifications_exists = response.xpath("//div[@class='product-classifications']").extract_first(default='empty-tab')
        if is_specifications_exists != 'empty-tab':
            for row in response.xpath('//*[@id="home"]/div[2]/table/tbody/tr'):
                current_specification = {}

                specification_title = row.xpath('.//td[1]/text()').extract_first().strip()
                specification_title = specification_title.replace('\n', '')
                specification_title = specification_title.replace('\t', '')

                specification_text = row.xpath('.//td[2]/text()').extract_first().strip()
                specification_text = specification_text.replace('\n', '')
                specification_text = specification_text.replace('\t', '')

                current_specification[specification_title] = specification_text

                print(current_specification)
                products_specifications.append(current_specification)
            pass
        else:
            is_other_information_exists = response.xpath('//div[@class="tab-details"]').extract_first(default='empty-tab')
            if is_other_information_exists != 'empty-tab':
                additional_information_box = {}
                additional_product_information = response.xpath('//*[@id="profile"]/div/p/text()').extract_first().strip()
                additional_information_box["Additional_information"] = additional_product_information
                products_specifications.append(additional_information_box)
            else:
                no_information_box = {}
                no_specifications = response.xpath('//*[@id="home"]/div[2]/text()').extract_first().strip()
                no_information_box["No_information_found"] = no_specifications
                products_specifications.append(no_information_box)
        # END of product specifications

        product['specifications'] = products_specifications

        yield product
