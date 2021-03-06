# -*- coding: utf-8 -*-
import re
from urllib import parse
from paperSpider.utils.common import format_word
import scrapy
from scrapy import Request
from paperSpider.items import PaperspiderItem
from scrapy_redis.spiders import RedisSpider


class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    # redis_key = 'baidu:start_urls'
    allowed_domains = ['xueshu.baidu.com']
    input_keyword = 'machine%20learning'
    start_urls = [
        # 'http://xueshu.baidu.com/s?wd=machine%20learning&pn=0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_f_para=sc_tasktype%3D%7BfirstAdvancedSearch%7D&sc_hit=1'
        # 'http://xueshu.baidu.com/s?wd=%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0&tn=SE_baiduxueshu_c1gjeupa&cl=3&ie=utf-8&bs=machine+learning&f=8&rsv_bp=1&rsv_sug2=0&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&rsv_spt=3'
        # 'http://xueshu.baidu.com/s?wd=%E6%95%B0%E6%8D%AE%E6%8C%96%E6%8E%98&rsv_bp=0&tn=SE_baiduxueshu_c1gjeupa&rsv_spt=3&ie=utf-8&f=8&rsv_sug2=0&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D'
        'http://xueshu.baidu.com/s?wd=%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0&tn=SE_baiduxueshu_c1gjeupa&cl=3&ie=utf-8&bs=%E6%95%B0%E6%8D%AE%E6%8C%96%E6%8E%98&f=8&rsv_bp=1&rsv_sug2=0&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&rsv_spt=3'
    ]

    def parse(self, response):
        paper_nodes = response.xpath('//*[@class="sc_content"]')
        for paper_node in paper_nodes:
            paper_url = paper_node.css('h3 a::attr(href)').extract_first('')
            yield Request(url=parse.urljoin(response.url, paper_url), callback=self.parse_detail)

        next_url = response.css('#page a:last-child::attr(href)').extract_first('')
        if next_url:
            # next_url = 'http://xueshu.baidu.com' + next_url
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        paper_item = PaperspiderItem()

        paper_title = response.css('.main-info h3 a::text').extract_first('')
        paper_title = format_word(paper_title)

        paper_writer = response.css('.author_wr .author_text span a::text').extract()
        paper_abstract = response.css('.abstract::text').extract_first('')
        paper_keywords = response.css('.kw_wr .kw_main span a::text').extract()

        paper_DOI = response.css('.doi_wr .kw_main::text').extract_first('')
        paper_DOI = format_word(paper_DOI)

        paper_cite_count = response.css('.sc_cite_cont::text').extract_first(0)
        paper_cite_count = format_word(paper_cite_count)

        paper_source = response.css('.love_wr .label-ll a::attr(href)').extract_first('')

        paper_time = response.css('.year_wr .kw_main::text').extract_first('暂无')
        paper_time = format_word(paper_time)

        paper_download_link = response.css('#savelink_wr .dl_item_span a::attr(href)').extract()

        paper_item['paper_title'] = paper_title
        paper_item['paper_writer'] = paper_writer
        paper_item['paper_abstract'] = paper_abstract
        paper_item['paper_keywords'] = paper_keywords
        paper_item['paper_DOI'] = paper_DOI
        paper_item['paper_time'] = paper_time
        paper_item['paper_cite_count'] = paper_cite_count
        paper_item['paper_source'] = paper_source
        paper_item['paper_download_link'] = paper_download_link[:5]

        yield paper_item
