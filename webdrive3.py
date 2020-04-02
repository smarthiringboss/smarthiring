# -*- coding:utf-8 -*-
from urllib import  request, error
import requests
from lxml import etree
import  csv
import queue as Queue
import threading
import time
import pandas as pd
import re
from datetime import datetime, date, timedelta
from lxml import etree
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium import webdriver
from bs4 import BeautifulSoup
import threading

queue = Queue.Queue()#存放网址的队列
out_queue = Queue.Queue()#存放网址页面的队列

class Get_xinxi(threading.Thread):
    def __init__(self,x):
        threading.Thread.__init__(self)
        self.x = x

    def run(self):
        chromeOptions = Options()
        # 添加debuggerAddress这个属性 可以操控我手动打开的浏览器（不过要事先开启用doc命令开启浏览器的远程调试而且端口与这个一样）
        chromeOptions.add_experimental_option('debuggerAddress', self.x)
        # 最终装饰成浏览器可以去发送解析url
        browser = webdriver.Chrome(options=chromeOptions)
        while True:
            xinxi = queue.get()
            browser.get(xinxi[4])
            print(xinxi[0],xinxi[1],xinxi[2])
            time.sleep(1)
            ActionChains(browser).move_to_element(browser.find_element_by_xpath(
                "//div[@class='filter-select-box']/div[6]/span")).perform()  # 鼠标class=filter-select-box的div标签下的第六个div标签下的span标签
            browser.find_element_by_xpath("//a[@ka='sel-scale-3']").click()  # 点击属性ka=sel-scale-1的a标签
            time.sleep(1)
            while True:
                try:
                    # 用BeautifulSoup提取解析url以后的html文件
                    soup = BeautifulSoup(browser.page_source, 'lxml')
                    # 查找所有class=job-title的标签放入一个列表
                    gangweis = soup.select('.job-title .job-name')
                    # gangweis = html.xpath("//div[@class='job-title']/span[@class='job-name']")[0]
                    # 查找所有class=company-text的标签下的a标签放入一个列表
                    gongsis = soup.select('.company-text a')
                    # 公司所属行业 融资状况  规模
                    sanges = soup.select(".company-text p")
                    # 查找所有class=info-primary的标签下的P标签放入一个列表
                    xuelis = soup.select('.job-limit p')
                    jingyans = soup.select('.job-limit  p')
                    # 查找所有class=red的span 标签放入一个列表
                    xinzis = soup.find_all('span', attrs={'class': 'red'})
                    # 查找所有class=info-primary的标签下的P标签放入一个列表
                    chengshis = soup.select('.job-area-wrapper .job-area')
                    # 查找所有class=info-publis的p标签放入一个列表
                    riqis = soup.select('.job-title .job-pub-time')
                    s = (date.today() + timedelta(days=0)).strftime("%Y/%m/%d")
                    x = "_".join(s.split("/"))
                    xinxi[0] = "、".join(xinxi[0].split("/"))
                    xinxi[1] = "_".join(xinxi[1].split("/"))
                    filename = 'C:/Users/t/Desktop/初始数据/' + xinxi[0] + '/' + xinxi[1] + '/' + xinxi[1] + x + '.csv'
                    # 以写的形式打开文件 newline为空  防止出现多余的空行
                    with open(filename, 'a', encoding='utf-8', newline='') as csvfile:
                        # 创建一个操作此文件的对象
                        writer = csv.writer(csvfile)
                        # 对得到的数据压缩（因为数据都是一样的条数且一一对应的）以后再对它迭代
                        for gangwei, gongsi, sange, xueli, jingyan, xinzi, chengshi, riqi in zip(gangweis, gongsis, sanges,
                                                                                                 xuelis, jingyans, xinzis,
                                                                                                 chengshis,riqis,):
                            gongsihangye = sange.contents[0]
                            #去除职位中的异常符号
                            gangwei = "".join(re.findall('\w+|/|.|\s|\\+',gangwei.get_text()))
                            gangwei = "_".join(gangwei.split(","))
                            if len(xueli.contents)>2:
                                xueli = xueli.contents[-1]
                            else:
                                continue
                            writer.writerow(
                                [gangwei, gongsi.get_text(), gongsihangye, sange, sange, xueli,
                                 jingyan.contents[0], xinzi.get_text(), chengshi.contents[0], riqi.get_text(),
                                 xinxi[2]])
                    # 如果html中有next disabled说明已经到最后一页 就退出循环
                    if browser.page_source.find('next disabled') != -1:
                            break
                    if browser.page_source.find('next') == -1:
                            break
                        # 滚动条向下滚动2500像素
                    browser.execute_script("window.scrollTo(0,10000);")
                    time.sleep(1.5)
                    # 鼠标点击next的标签
                    browser.find_element_by_class_name('next').click()
                except:
                    queue.task_done()
                    queue.put(xinxi)
                    quit()
            queue.task_done()
            if queue.empty():
                break

class Controlle_thread(threading.Thread):

    def __init__(self, threads):
        threading.Thread.__init__(self)
        self.threads = threads


    def run(self):
        for i in self.threads:
            i.start()

        ip_list = ['127.0.0.1:9223','127.0.0.1:9224','127.0.0.1:9225']
        while True:
            for a in range(3):
                if not self.threads[a].isAlive():
                    print("a")
                    self.threads[a] = Get_xinxi(ip_list[a])
                    self.threads[a].start()
            time.sleep(60*30)
            print("检查完成")
            if queue.empty():
                time.sleep(120)
                print("本次结束")
                break


if __name__ == '__main__':
    df = pd.read_csv('Bossaa.csv', sep=',', encoding='utf-8')
    df.drop_duplicates(subset='suoshuhangye', inplace=False, keep="first")
    xinxis = []
    for shuxing, suoshuhangye, gangweimingcheng, gangweiwangzhi in zip(df['shuxin'], df['suoshuhangye'],
                                                                       df['gangweimingcheng'],
                                                                       df['gangweiwangzhi']):
        url = gangweiwangzhi + '?period=2?page=1&ka=page-1'
        xinxi = [shuxing, suoshuhangye, gangweimingcheng, gangweiwangzhi, url]
        queue.put(xinxi)

    threads = []

    # 创建线程
    for i in ['127.0.0.1:9223','127.0.0.1:9224','127.0.0.1:9225']:
        x = i
        x = i
        dt = Get_xinxi(x)
        threads.append(dt)

    x = Controlle_thread(threads)
    x.start()
    x.join()