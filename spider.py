 from lxml import etree
import requests
import csv
import time


def spider():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    pre_url = 'https://fuzhou.58.com/ershoufang/pn'
    for x in range(1,11):
        html = requests.get(pre_url+str(x),headers = headers)
        html.encoding = 'utf-8'
        time.sleep(1)
        selector = etree.HTML(html.text)
        house_list = selector.xpath('/html/body/div[5]/div[5]/div[1]/ul/li')
        for house in house_list:
            introduce = house.xpath("div[2]/h2/a/text()")
            name = house.xpath("div[2]/p[2]/span/a[1]/text()")
            layout = house.xpath('div[2]/p[1]/span[1]/text()')
            area = house.xpath('div[2]/p[1]/span[2]/text()')
            region = house.xpath('div[2]/p[2]/span/a[3]/text()')
            total_price = house.xpath('div[3]/p[1]/b/text()')
            item = [introduce,name,layout,area,region,total_price]
            data_writer(item)
            print('正在抓取:{}'.format(name))
def data_writer(item):
    with open('抚州二手房信息.csv','a',encoding='utf-8',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(item)
if __name__ == '__main__':
    spider()
