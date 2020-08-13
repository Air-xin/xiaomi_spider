import scrapy
import requests
from fake_useragent import UserAgent
import json
from xiaomiSpider.items import XiaomispiderItem


class XiaomiSpiderSpider(scrapy.Spider):
    name = 'xiaomi_spider'
    allowed_domains = ['app.mi.com']
    start_urls = ['http://app.mi.com/']

    def __init__(self):
        super().__init__()
        self.one_url = 'http://app.mi.com/categotyAllListApi?page={}&categoryId={}&pageSize=30'
        self.two_url = 'http://app.mi.com/details?id={}'

    def parse(self, response):
        """解析首页，获取分类应用"""
        li_list = response.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li/a/@href')
        # print('-------------------------------')
        # print(li_list)
        application_type_list = response.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li/a/text()')
        for i in range(len(li_list)):
            item = XiaomispiderItem()
            id = li_list[i].get().split('/')[-1]
            # print('aaaaaaaaaaaaaaaaaaaaaa')
            # print(id)
            item['type'] = application_type_list[i].get()
            count = self.get_count(id)
            page = self.get_page(count)
            for i in range(page):
                url = self.one_url.format(i, id)
                yield scrapy.Request(url=url, callback=self.two_parse, meta={'item': item})

    def get_count(self, id):
        """
        获取分类下应用数量
        :param id: 应用码号
        :return: 应用数量
        """
        url = self.one_url.format(0, id)
        json_str = requests.get(url=url, headers={'User-Agent': UserAgent().random}).text
        count = json.loads(json_str)['count']
        return count

    def get_page(self, count):
        """
        获取分类应用下页码数
        :param count: 分类应用下的应用数量
        :return: 页码数
        """
        page = count // 30 if count % 2 == 0 else count // 30 + 1
        return page

    def two_parse(self, response):
        """解析分类应用下每页应用"""
        item1 = response.meta['item']
        data = json.loads(response.text)['data']
        for i in data:
            item = XiaomispiderItem()
            item['name'] = i['displayName']
            item['type'] = item1['type']
            link = self.two_url.format(i['packageName'])
            yield scrapy.Request(url=link, callback=self.three_parse, meta={'item': item})

    def three_parse(self, response):
        """提取应用信息"""
        item1 = response.meta['item']
        item = XiaomispiderItem()
        item['name'] = item1['name']
        item['type'] = item1['type']
        score = int(
            response.xpath('/html/body/div[6]/div[1]/div[2]/div[1]/div/div[1]/div/@class').get().split(' ')[-1].split(
                '-')[-1])
        score = score // 2 if score % 2 == 0 else score // 2 + 0.5
        item['score'] = score
        item['score_num'] = int(
            response.xpath('/html/body/div[6]/div[1]/div[2]/div[1]/div/span/text()').get().split(' ')[1][:-3])
        yield item
