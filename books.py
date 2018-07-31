import time
import lxml
import lxml.etree
import requests
import re
from concurrent.futures import ThreadPoolExecutor  # 线程池


def getHtml(url, header):
    try:
        proxyPasswd = {'http': 'http://182.112.117.80:8118'}
        req = requests.get(url, headers=header, proxies=proxyPasswd, timeout=30)
        req.raise_for_status()
        response = req.text
        return response
    except:
        return '没找到页面'


def getUrlList(response):
    try:
        mytree = lxml.etree.HTML(response)
        typeUrl = mytree.xpath('//ul[@id="zg_browseRoot"]/ul/ul/li/a/@href')
        typeName = mytree.xpath('//ul[@id="zg_browseRoot"]/ul/ul/li/a/text()')
        urlDict = {}
        for i in range(len(typeName)):
            urlDict[typeName[i]] = typeUrl[i]
        return urlDict
    except:
        return 'qqq'


def getPageList(response):
    mytree = lxml.etree.HTML(response)
    pageUrl = mytree.xpath('//ol[@class="zg_pagination"]/li/a/@href')
    return pageUrl


def getInfo(response):
    mytree = lxml.etree.HTML(response)
    try:
        # 图书排名
        sort = mytree.xpath('//span[@class="zg_rankNumber"]/text()')
        # 去除空字符
        bookSort = []
        for i in sort:
            s = i.strip()[:-1]
            bookSort.append(s)

        # 书名
        bookName = mytree.xpath('//img[@class="a-thumbnail-left"]/@alt')
        # 书的图片地址
        bookPic = mytree.xpath('//img[@class="a-thumbnail-left"]/@src')
        # 作者
        author = mytree.xpath('//span[@class="a-size-small a-color-base"]/text()')
        # 价格
        price = mytree.xpath('//div[@class="a-fixed-left-grid-col a-col-right"]/div/a/span/span/text()')

        bookInfoList = []
        for i in range(len(bookSort)):
            bookInfoList.append(str((bookSort[i], bookName[i], bookPic[i], author[i], price[i])))
        return bookInfoList

    except Exception as e:
        return e


def saveInfo(name, list):
    path = name + ".txt"
    # 写入txt文件
    for i in list:
        print(i)
        with open(path, 'a+', encoding='utf-8', errors="ignore") as f:
            f.write(i + '\n')
            f.flush()


if __name__ == '__main__':

    #亚马逊各类图书排行榜前100名
    startURL = 'https://www.amazon.cn/gp/bestsellers/books/ref=zg_bs_books_home_all'
    header = {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36"
    }
    response = getHtml(startURL, header)

    urlDict = getUrlList(response)

    time.clock()
    with ThreadPoolExecutor(5) as exT:

        for bookType, sonUrl in urlDict.items():
            html = getHtml(sonUrl, header)
            pageUrlList = getPageList(html)
            for pageUrl in pageUrlList:
                html = getHtml(pageUrl, header)
                infoList = getInfo(html)
                exT.submit(saveInfo, bookType, infoList)
    print(time.clock())
