# !/usr/bin/env python
# -*-encoding: utf-8-*-
# author:LiYanwei
# version:0.1

import time
from multiprocessing.dummy import Pool as Threadpool
import sys
import requests
from lxml import etree
import json
import pymongo
import xlsxwriter
import os

reload(sys)
sys.setdefaultencoding("utf-8")

def get_response(url):
    proxies = {
        'http': 'http://210.38.1.139:8080'
    }
    html = requests.get(url, headers = headers, proxies = proxies)
    selector = etree.HTML(html.text)
    product_list = selector.xpath('//*[@id="J_goodsList"]/ul/li') # .//*[@id='J_goodsList']/ul/li
    for product in product_list:
        try:
            sku_id = product.xpath('@data-sku')[0]
            product_url = 'https://item.jd.com/{}.html'.format(str(sku_id))
            get_data(product_url)
        except Exception as e:
            print e


def get_data(url):
    '''
    获取商品的详情
    :param url:
    :return:
    '''
    product_dict = {}
    print url
    proxies = {
        'http': 'http://210.38.1.134:8080'
    }
    html = requests.get(url, headers = headers, proxies = proxies)
    selector = etree.HTML(html.text)
    product_infos = selector.xpath('//ul[@class="parameter2 p-parameter-list"]')
    for product in product_infos:
        product_number = product.xpath('li[2]/@title')[0]
        product_name = product.xpath('li[1]/@title')[0]
        product_place = product.xpath('li[4]/@title')[0]
        product_price = get_product_price(product_number)
        # print product_number, product_name, product_place, product_price

        product_dict['商品名称'] = product_name
        product_dict['商品id'] = product_number
        product_dict['商品产地'] = product_place
        product_dict['商品价格'] = product_price

    save(product_dict)


def get_product_price(sku):
    '''
    获取价格
    :param sku:
    :return:
    '''
    # https://p.3.cn/prices/mgets?skuIds=J_4938580
    price_url = 'https://p.3.cn/prices/mgets?skuIds=J_{}'.format(str(sku))
    proxies = {
        'http': 'http://183.222.102.102:8080'
    }
    response = requests.get(price_url, headers = headers, proxies =proxies).content
    response_json = json.loads(response)
    for info in response_json:
        return info.get('p')


def save(product_list):
    '''
    保存数据到数据库
    :param list:
    :return:
    '''
    client = pymongo.MongoClient('localhost')
    db = client['product_dict']
    content = db['jd']
    content.insert(product_list)


if __name__ == '__main__':
    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:54.0) Gecko/20100101 Firefox/54.0'
    }
    urls = ['https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&suggest=1.def.0.V00&wq=shouji&cid2=653&cid3=655&page={}&s=57&click=0'.format(page) for page in range(1,page_num*2,2)]
    start_time = time.time()
    pool = Threadpool(5)
    pool.map(get_response,urls)
    pool.close()
    pool.join()
    end_time = time.time()
    print u'用时()秒'.format(str(end_time - start_time))


# def print_hello(name):
#     print 'Hello',name
#     time.sleep(2) # 延时
#
# name_list = ['tony','xiao','lvshe']
# start_time =  time.time()
# pool = Threadpool(3) # 创建线程池池 参数是线程的个数
# pool.map(print_hello, name_list) # map 映射 能接受一个方法,一个序列
# pool.close()
# pool.join() # 主线程等待子线程结束
# end_time = time.time()
#
# print  '%d second' %(end_time - start_time)