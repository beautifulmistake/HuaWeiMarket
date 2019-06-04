# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HuaweimarketredisItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    # 关键字
    keyword = scrapy.Field()
    # APP名称
    app_name = scrapy.Field()
    # APP 描述
    app_desc = scrapy.Field()
    # 发布日期
    publishTime = scrapy.Field()
    # APP开发者
    author = scrapy.Field()
    # APP下载次数
    downloads = scrapy.Field()
    # APP图片链接
    app_pic = scrapy.Field()
    # APP详情页链接
    detail_page = scrapy.Field()
    # APP种类
    category = scrapy.Field()
    # APP大小
    file_size = scrapy.Field()
    # APP版本号
    version = scrapy.Field()
    # APP评分
    averageRating = scrapy.Field()
    # APP评论数
    commentNum = scrapy.Field()
