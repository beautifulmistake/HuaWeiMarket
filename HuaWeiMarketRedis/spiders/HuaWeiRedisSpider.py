import scrapy
import redis
from urllib import parse
import re
from scrapy_redis.spiders import RedisSpider
from HuaWeiMarketRedis.items import HuaweimarketredisItem
# 全局的变量，用于设定默认值
default_value = "null"
"""
根据关键字搜索采集华为应用市场的目标字段信息
"""


# 定义自己的爬虫类
class HuaWeiMarketSpider(RedisSpider):
    # 为爬虫命名
    name = "HuaWeiRedisSpider"
    redis_key = "HuaWeiRedisSpider:start_urls"
    # 初始化方法

    def __init__(self):
        # 与关键字拼接获取第一次的请求
        self.base_url = "https://appstore.huawei.com/search/{}/{}"
        # 添加user_agent,否则请求不到数据
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        }
        # 拼接详情页的url
        self.detail_page = "https://appstore.huawei.com"

    # 构造请求的初始url
    def start_requests(self):
        """
        连接redis获取关键字，构造初始的url
        :return:
        """
        connect = redis.Redis(host='127.0.0.1', port=6379, db=4, password='pengfeiQDS')  # 获取redis的连接
        keyword_total = connect.dbsize()    # 获取关键字总数
        # 遍历获取每一个关键字
        for index in range(360001, 480001):    # 测试时用代码
        #for index in range(keyword_total):
            # 使用get方法获取关键字
            keyword = connect.get(str(index)).decode('utf-8')
            # 将获取的关键字与base_url做拼接获取目标url
            target_url = self.base_url.format(parse.quote(keyword), str(1))
            # 将目标url加入爬取队列
            yield scrapy.FormRequest(url=target_url, callback=self.get_page,
                                     meta={"keyword": keyword, 'dont_redirect': True, 'handle_httpstatus_list': [301]}, headers=self.headers)

    # 解析搜索页面
    def get_page(self,response):
        """
        解析页面获取页面信息
        :param response:
        :return:
        """
        # 判断是否响应成功
        if response.status == 200:
            """
            获取页面，根据解析出的搜索商品总件数，
            分情况讨论是构造所有页号的url还是未匹配到任何结果
            将关键字写入无匹配结果的文件中
            """
            # 获取当前的关键字
            keyword = response.meta['keyword']
            # 解析出总条数,获取的为包含总条数的字符串，需正则匹配出数字，为字符串
            total_str = response.xpath('//div[@class="unit nofloat"]//p[@class="content"]//span[@class="sres"]/text()').extract_first()
            res = re.compile(r'\d+')    # 确定从字符串中匹配出数字的规则
            total = int(res.findall(total_str)[-1])  # 从字符串中匹配数字
            # 判断total的数值，如果为0则代表无搜索结果将该关键字写入无匹配结果的文件之中
            if total == 0:
                # 将关键字写入文件中
                with open('./无匹配结果.txt', 'a+', encoding='utf-8') as f:
                    f.write(keyword + "\n")
            elif total:
                # 计算出总页数
                pageNum = total // 23 + 1 if total % 23 else total // 23
                # 构造每一页的请求
                for index in range(1, pageNum+1):
                    # 将每一页的请求加入采集队列中
                    yield scrapy.FormRequest(url=self.base_url.format(parse.quote(keyword), str(index)),
                                             callback=self.get_first_page, meta={'keyword': keyword, 'dont_redirect': True, 'handle_httpstatus_list': [301]}
                                             , headers=self.headers)

    # 解析页面
    def get_first_page(self,response):
        # 判断是否响应成功
        if response.status == 200:
            """
           解析每个页号中每个APP的详情页链接
            """
            # 解析出详情页的链接
            detail_page_urls = response.xpath('//div[@class="game-info-ico"]/a/@href').extract()
            for detail_page_url in detail_page_urls:
                # 将获取的url做拼接获取详情页的链接
                detail_url = self.detail_page + detail_page_url
                # 将详情页链接加入meta属性中传递
                response.meta["detail_page_url"] = detail_page_url
                # 加入详情页的解析队列
                yield scrapy.FormRequest(url=detail_url, callback=self.get_detail_pages, meta=response.meta, headers=self.headers)

    # 解析详情页
    def get_detail_pages(self,response):
        """
        解析详情页的信息
        :param response:
        :return:
        """
        if response.status == 200:
            # 关键字
            keyword = response.meta['keyword']
            # APP名称
            app_name = response.xpath('//div[@class="app-info flt"]/ul[1]/li[2]/p/span[@class="title"]/text()').extract_first()
            # APP 描述
            app_desc = response.xpath('//div[@class="content"]/div[@id="app_strdesc"]/text()').extract_first()
            # 发布日期
            publishTime = response.xpath('//div[@class="app-info flt"]/ul[2]/li[2]/span/text()').extract_first()
            # APP开发者
            author = response.xpath('//div[@class="app-info flt"]/ul[2]/li[3]/span/@title').extract_first()
            # APP下载次数,需要切片获取[3:]
            downloads = response.xpath(
                '//div[@class="app-info flt"]/ul[1]/li[2]/p/span[@class="grey sub"]/text()').extract_first()
            # APP 图片链接
            app_pic = response.xpath('//div[@class="app-info flt"]/ul[1]/li[1]/img/@src').extract_first()
            # APP详情页链接
            detail_page_url = response.meta['detail_page_url']
            # APP种类,华为应用市场中并无此字段，故用默认值代替
            # APP大小
            file_size = response.xpath('//div[@class="app-info flt"]/ul[2]/li[1]/span/text()').extract_first()
            # APP版本号
            version = response.xpath('//div[@class="app-info flt"]/ul[2]/li[4]/span/text()').extract_first()
            # APP评分,需要切片[6:]
            averageRating = response.xpath('//div[@class="app-info flt"]/ul[1]/li[2]/p[2]/span/@class').extract_first()
            # APP评论数，华为应用市场也无，用默认值代替

            """
            在此处增加判断，如果APP名称或者APP的开发者中包含关键字则当前的item才执行写加入管道文件
            """
            # if keyword in app_name or keyword in author:
            # 创建item
            item = HuaweimarketredisItem()
            # 判断item是否为空
            item['keyword'] = keyword   # 关键字
            item['app_name'] = app_name if app_name else default_value  # APP名称
            item['app_desc'] = app_desc if app_desc else default_value  # APP描述
            item['publishTime'] = publishTime if publishTime else default_value  # APP上线时间
            item['author'] = author if author else default_value    # APP开发者
            item['downloads'] = downloads[3:] if downloads else default_value   # APP下载量
            item['app_pic'] = app_pic if app_pic else default_value     # APP图片
            item['detail_page'] = "http://app.hicloud.com" + detail_page_url   # APP详情页链接
            item['category'] = default_value    # APP种类
            item['file_size'] = file_size if file_size else default_value   # APP大小
            item['version'] = "V" + version if version else default_value  # APP版本号
            item['averageRating'] = averageRating[6:] + "分" if averageRating else default_value   # APP评分
            item['commentNum'] = default_value  # APP评论数
            yield item
