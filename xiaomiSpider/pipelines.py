# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv


class XiaomispiderPipeline:

    def open_spider(self, spider):
        self.f = open('xiaomi_application.csv', 'a')
        self.csv_writer = csv.writer(self.f)

        # 第一次爬取数据使用
        # self.csv_writer.writerow(['name','type','score','score_num'])

    def process_item(self, item, spider):
        print(dict(item))
        name = item['name']
        type = item['type']
        score = item['score']
        score_num = item['score_num']
        self.csv_writer.writerow([name, type, score, score_num])
        self.f.flush()
        return item

    def close_spider(self, spider):
        self.f.close()
