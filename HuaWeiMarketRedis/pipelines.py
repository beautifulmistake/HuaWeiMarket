# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from HuaWeiMarketRedis.utils import get_db
mongo_db = get_db()


class HuaweimarketredisPipeline(object):
    # 创建文件的方法
    def open_spider(self, spider):
        """
        在当前目录下创建文件，记录采集的数据
        :param spider:
        :return:
        """
        self.file = open('./华为应用市场测试数据.txt', 'a+', encoding='utf-8')  # 创建文件
    def process_item(self, item, spider):
        # 关键字
        keyword = item['keyword']
        print("查看获取的关键字=================：", keyword)
        # APP名称
        app_name = item['app_name']
        print("查看获取的APP名称================：", app_name)
        # APP 描述
        app_desc = item['app_desc']
        print("查看获取的APP描述================：", app_desc)
        # 发布日期
        publishTime = item['publishTime']
        print("查看获取的APP发布时间============：", publishTime)
        # APP开发者
        author = item['author']
        print("查看获取的APP开发者==============：", author)
        # APP下载次数
        downloads = item['downloads']
        print("查看获取的APP下载次数============：", downloads)
        # APP 图片链接
        app_pic = item['app_pic']
        print('查看获取的APP图片================：', app_pic)
        # APP详情页链接
        detail_page = item['detail_page']
        print('查看获取的APP详情================：', detail_page)
        category = item['category']
        print('查看获取的APP种类================：', category)
        # APP大小
        file_size = item['file_size']
        print("查看获取的APP大小================：", file_size)
        # APP版本号
        version = item['version']
        print("查看获取的APP版本号==============：", version)
        # APP评分
        averageRating = item['averageRating']
        print("查看获取的APP评分================：", averageRating)
        comment = item['commentNum']
        print("查看获取的APP评论数==============：", comment)
        # 将采集的目标字段整理成统一格式，定义变量接收拼接的结果
        result_content = ""
        result_content = result_content.join(
            keyword + "ÿ" + app_name + "ÿ" + app_desc + "ÿ" + publishTime + "ÿ" + author + "ÿ" +
            downloads + "ÿ" + app_pic + "ÿ" + detail_page + "ÿ" + category + "ÿ" + file_size + "ÿ" + version + "ÿ" +
            averageRating + "ÿ" + comment + "ÿ" + "\n"
        )
        # 将采集的数据写入文件
        self.file.write(result_content)
        self.file.flush()
        return item
    # 关闭文件的方法
    def close_spider(self, spider):
        """
        将采集的数据写入文件完成后，关闭文件
        :param spider:
        :return:
        """
        # 关闭文件
        self.file.close()


# 以下代码是存储到 mongodb时需要的代码
class ResultMongoPipeline(object):
    """抓取结果导入 mongo"""

    def __init__(self, settings):
        self.collections_name = settings.get('RESULT_COLLECTIONS_NAME')

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)

    def process_item(self, item, spider):
        mongo_db[self.collections_name].insert(item)
        return item

