# !/usr/bin/env python
# -*-encoding: utf-8-*-
# author:LiYanwei
# version:0.1

import requests
import sys
import os
import xlsxwriter
from selenium import webdriver
from lxml import etree
import re


# 中文编码设置
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

# 商品url汇总表
url_list = []

def main(work, key, num, mkname, page_num):
    # print type(num),num
    if num == '1':
        url = '''https://s.m.taobao.com/search?event_submit_do_new_search_auction=1\
        &_input_charset=utf-8&topSearch=1&atype=b&searchfrom=1&action=home%3Aredirect_app_action&\
        from=1&q=''' + key + '''&sst=1&n=20&buying=buyitnow&m=api4h5&abtest=10&wlsort=10&page=''' + str(page_num)
    else:
        url = '''https://s.m.taobao.com/search?event_submit_do_new_search_auction=1\
        &_input_charset=utf-8&topSearch=1&atype=b&searchfrom=1&action=home%3Aredirect_app_action&\
        from=1&q=''' + key + '''&sst=1&n=20&buying=buyitnow&m=api4h5&abtest=14&\
        wlsort=14&style=list&closeModues=nav%2Cselecthot%2Conesearch&sort=_sale&page=''' + str(page_num)

    try:
        body = requests.get(url)
        body = body.text.encode('utf8')
        dic_body = eval(body)
    except Exception, e:
        print "请求出错"
        print url
        print e


    for i in range(20):
        print "当前正在采集第", i + 1, "个,第", str(page_num), '页'
        try:
            num_id = dic_body["listItem"][i]['item_id']
        except:
            num_id = ''
        try:
            act = dic_body["listItem"][i]['act']  # 付款数
        except:
            act = ''
        try:
            area = dic_body["listItem"][i]['area']  # 地区
        except:
            area = ''
        try:
            if dic_body["listItem"][i]['url'].find('https:') != -1:
                auctionURL = dic_body["listItem"][i]['url']  # 商品url
            else:
                auctionURL = "https:" + dic_body["listItem"][i]['url']  # 商品url
                # https://detail.tmall.com/item.htm?id="+str(num_id)
            # print len(auctionURL)
            if(len(auctionURL) > 250):
                auctionURL_1 = auctionURL[:250]
                auctionURL_2 = auctionURL[250::]
            else:
                auctionURL_1 = auctionURL
                auctionURL_2 = ''
        except:
            auctionURL = ''
            auctionURL_1 = ''
            auctionURL_2 = ''
        try:
            name = dic_body["listItem"][i]['name']  # 商品名
        except:
            name = ''
        try:
            nick = dic_body["listItem"][i]['nick']  # 店铺名
        except:
            nick = ''
        try:
            originalPrice = dic_body["listItem"][i]['originalPrice']  # 原始价格
        except:
            originalPrice = ''
        try:
            price = dic_body["listItem"][i]['price']  # 当前价格
        except:
            price = ''
        try:
            pic_path = dic_body["listItem"][i]['pic_path']  # 当前价格
            # print pic_path
            pic_path = pic_path.replace('60x60', '210x210')
            pic_name = str(i + 1 + (page_num - 1) * 20) + '-' + nick
            img_download(pic_name, pic_path, mkname + '/pic')
        except Exception, e:
            print e
            pic_path = ''
        try:
            zkType = dic_body["listItem"][i]['zkType']  # 当前价格
        except:
            zkType = ''
        try:
            if len(auctionURL_2) > 10:
                first = 0
                html_date = download_date(
                    auctionURL_1 + auctionURL_2, work, i + 2, first)
            else:
                first = 0
                html_date = download_date(auctionURL_1, work, i + 2, first)
        except:
            html_date = ''
        # print html_date
        date = [name, nick, act, price, originalPrice, zkType, area,
                auctionURL_1, auctionURL_2, pic_path, html_date, num_id]
        print len(date)
        num = i + 2 + (int(page_num) - 1) * 20
        install_table(date, work, num)
    # 商品名 店铺 付款人数 当前价格 原始价格 优惠类型 地区 商品url  图片url  详情数据#
    # name nick act price originalPrice zkType area auctionURL pic_path html_date


def download_date(url, work, i, first):
    # if first == 1:
    '''导入商品url，进行详情页面解析'''
    if(url.find("taobao") != -1 and first != 1):
        print "检测为淘宝的页面"
        try:
            driver = webdriver.PhantomJS()
            print "正在获取详情页面,url为"
            #url ="https://item.taobao.com/item.htm?id=538287375253&abtest=10&rn=07abc745561bdfad6f726eb186dd990e&sid=46f938ba6d759f6e420440bf98b6caea"
            url = url
            # print url
            driver.get(url)
            driver.implicitly_wait(40)  # 设置智能超时时间
            html = driver.page_source.encode('utf-8')
            driver.quit()
        except Exception, e:
            print "页面加载失败", e
            return 0
        try:
            print '正在解析页面'
            try:
                selector = etree.HTML(
                    html, parser=etree.HTMLParser(encoding='utf-8'))
            except Exception, e:
                print "页面加载失败", e
                return 0

            try:  # 此部分用于采集每月销量的数据
                print '正在解析页面1'
                # context=selector.xpath('//div[@class="tm-indcon"]')
                context = selector.xpath('//strong[@id="J_SellCounter"]')
                xiaoliang_date = u''
                for i in range(len(context)):
                    print '正在解析页面2'
                    temp_date = etree.tostring(
                        context[i], encoding="utf-8")  # .encode('utf-8')
                    print '***', temp_date
                    # 去除一切html标签 attributes-list
                    re_h = re.compile('</?\w+[^>]*>')
                    s = re_h.sub('', temp_date) + ','
                    xiaoliang_date += s
                print '正在解析页面3'
                list_date = xiaoliang_date + ';'
            except Exception, e:
                print e
                list_date = u''
            context = selector.xpath('//ul[@class="attributes-list"]/li')
            for i in range(len(context)):  # attributes-list
                # .encode('utf-8')
                a = etree.tostring(context[i], encoding="utf-8")
                b = a.split('>')
                end = b[1].split('<')[0] + ';'
                list_date += end
            print '&&&&&&&&&&&', list_date.encode('utf8')
            if len(list_date) < 50:
                print "数据过少，尝试检测为天猫页面解析"
                try:
                    driver = webdriver.PhantomJS()
                    print "正在获取详情页面,url为"
                    #url ="https://item.taobao.com/item.htm?id=538287375253&abtest=10&rn=07abc745561bdfad6f726eb186dd990e&sid=46f938ba6d759f6e420440bf98b6caea"
                    #num_id = re.findall('id=[0-9]+&',url)[0].replace('id=','').replace('&','')
                    #url = "https://detail.tmall.com/item.htm?id="+str(num_id)
                    print url
                    driver.get(url)
                    driver.implicitly_wait(40)  # 设置智能超时时间
                    html = driver.page_source.encode('utf-8')
                    driver.quit()
                except Exception, e:
                    print "页面加载失败", e
                    return 0
                try:
                    print '正在解析页面'
                    try:
                        selector = etree.HTML(
                            html, parser=etree.HTMLParser(encoding='utf-8'))
                    except Exception, e:
                        print "页面加载失败", e
                        return 0
                    try:
                        # 此部分用于采集每月销量的数据
                        context = selector.xpath('//div[@class="tm-indcon"]')
                        xiaoliang_date = u''
                        for i in range(len(context)):
                            temp_date = etree.tostring(
                                context[i], encoding="utf-8")  # .encode('utf-8')
                            re_h = re.compile('</?\w+[^>]*>')  # 去除一切html标签
                            s = re_h.sub('', temp_date) + ','
                            xiaoliang_date += s
                        list_date += xiaoliang_date + ';'
                    except Exception, e:
                        print e
                        list_date += u''

                    context = selector.xpath('//ul[@id="J_AttrUL"]/li')
                    print list_date, len(context)
                    for i in range(len(context)):
                        # .encode('utf-8')
                        a = etree.tostring(context[i], encoding="utf-8")
                        b = a.split('>')
                        end = b[1].split('<')[0] + ';'
                        list_date += end
                    # print list_date.encode('utf8')
                    return list_date
                except Exception, e:
                    print '页面解析失败'
                    return 0

            return list_date
        except:
            print '页面解析失败'
            return 0

    elif(url.find("tmall") != -1 and first != 1):
        print "检测为天猫页面，"
        try:
            driver = webdriver.PhantomJS()
            print "正在获取详情页面,url为"
            #url ="https://item.taobao.com/item.htm?id=538287375253&abtest=10&rn=07abc745561bdfad6f726eb186dd990e&sid=46f938ba6d759f6e420440bf98b6caea"
            num_id = re.findall(
                'id=[0-9]+&', url)[0].replace('id=', '').replace('&', '')
            url = "https://detail.tmall.com/item.htm?id=" + str(num_id)
            print url
            driver.get(url)
            driver.implicitly_wait(40)  # 设置智能超时时间
            html = driver.page_source.encode('utf-8')
            driver.quit()
        except Exception, e:
            print "页面加载失败", e
            return 0
        try:
            print '正在解析页面'
            try:
                selector = etree.HTML(
                    html, parser=etree.HTMLParser(encoding='utf-8'))
            except Exception, e:
                print "页面加载失败", e
                return 0
            try:
                # 此部分用于采集每月销量的数据
                context = selector.xpath('//div[@class="tm-indcon"]')
                xiaoliang_date = u''
                for i in range(len(context)):
                    temp_date = etree.tostring(
                        context[i], encoding="utf-8")  # .encode('utf-8')
                    re_h = re.compile('</?\w+[^>]*>')  # 去除一切html标签
                    s = re_h.sub('', temp_date) + ','
                    xiaoliang_date += s
                list_date = xiaoliang_date + ';'
            except Exception, e:
                print e
                list_date = u''

            context = selector.xpath('//ul[@id="J_AttrUL"]/li')
            print list_date, len(context)
            for i in range(len(context)):
                # .encode('utf-8')
                a = etree.tostring(context[i], encoding="utf-8")
                b = a.split('>')
                end = b[1].split('<')[0] + ';'
                list_date += end
            # print list_date.encode('utf8')
            return list_date
        except Exception, e:
            print '页面解析失败'
            return 0

def install_table(date, work, i):
    '''导入数据列表存入表格中 '''
    str_list = ['B', 'C', 'D', 'E', 'F', 'G',
                'H', 'I', 'J', 'K', 'L', 'M', "O"]
    #global worksheet1
    try:
        work.write('A' + str(i), int(i) - 1)
    except Exception, e:
        print '无法写入'
        print e
    for now_str, now_date in zip(str_list, date):
        num = now_str + str(i)
        try:
            work.write(num, now_date)
        except Exception, e:
            print "无法写入"
            print e


def img_download(id, url, mkname):
    '''导入图片url，文件夹名，以id为图片名'''
    try:
        print "主图下载中" + url
        #img = requests.get(url).context()
        name = id
        r = requests.get(url, timeout=50)
        #name = int(time.time())
        f = open('./' + mkname + '/' + str(name) + '.jpg', 'wb')
        f.write(r.content)
        f.close()
    except:
        print "主图下载失败"


def create_mkdir(name):
    '''创建文件夹'''
    try:
        print "开始创建文件夹 ", name
        os.mkdir(r'./' + name)
        os.mkdir(r'./' + name + "/pic")
    except Exception, e:
        print e


def create_table(name):
    ''' 导入表格名字，在当前目录下创建该表格'''
    try:
        name = './' + name + '/' + name + '.xlsx'

        workbook = xlsxwriter.Workbook(name)
        worksheet1 = workbook.add_worksheet()
        worksheet1.write('A1', 'ID')
        worksheet1.write('B1', u"商品名")
        worksheet1.write('C1', u'店铺')
        worksheet1.write('D1', u'付款人数')
        worksheet1.write('E1', u'当前价格')
        worksheet1.write('F1', u'原始价格')
        worksheet1.write('G1', u'优惠类型')
        worksheet1.write('H1', u'地区')
        worksheet1.write('I1', u'商品url_1')
        worksheet1.write('J1', u'商品url_2')
        worksheet1.write('K1', u'图片url')
        worksheet1.write('L1', u'date')
        worksheet1.write('M1', u'宝贝id')
        # workbook.close()
        print '表格构建完成,name', name
        return worksheet1, workbook
    except Exception, e:
        print e


if __name__ == '__main__':
    # 商品名称
    key = u'电脑'
    # 文件夹名称
    name = u'电脑'
    # 排序方式 1 为综合排序 2 为销量排序
    num = 1
    # 采集页数
    page_num = 1
    if (key == '' or name == '' or num == ''):
        print '参数不正确'
    else:
        # 创建文件夹
        create_mkdir(name)
        # 创建表格
        work, workbook = create_table(name)
        print '开始采集请等待'
        for now_page_num in range(1, page_num + 1):
            main(work, key, num, name, now_page_num)
        workbook.close()
        print '采集完成'