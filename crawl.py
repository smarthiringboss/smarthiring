import time
import requests
from requests import Session
from http import client
import re
from lxml import etree
import json
import random
import pymysql
from bs4 import BeautifulSoup


client._is_legal_header_name = re.compile (br':|\A[^:\s][^:\r\n]*\Z').match


class BossSpider () :
    session = Session ()
    num = 0
    company = {
        'zhifubao' : '1f8227007663695b3nV63Q~~',
        'baidu' : 'ab9fdc6f043679990HY~',
        'tenxun' : '2e64a887a110ea9f1nRz',
        'ali' : '5d627415a46b4a750nJ9',
        'zijietiaodong' : 'a67b361452e384e71XV82N4~',
        'huawei' : '02cd05cce753437e33V50w~~',
        'wangyi' : '821662f4a993420c3nZ62dg~',
        'jindong' : '755f9f2f1799f89a03d60g~~',
        'mayi' : 'e9a2427bc19f1b1a33Z_3t0~',
        'jdjituan' : '33e052361693f8371nF-3d25',
        'BJzijie' : '7d01ce6cfe2022030HJ409y-',
        'bjtenxun' : '0979070fc97e501a0nx7'
    }
    USER_AGENT_LIST = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]

    def __init__(self) :
        self.proxy = self.get_proxy ()
        self.agent = random.choice (self.USER_AGENT_LIST)
        self.headers = {
            ':authority' : 'www.zhipin.com',
            ':method' : 'GET',
            # ':path': urlb,
            ':scheme' : 'https',
            'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding' : 'gzip, deflate, br',
            'accept-language' : 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cache-control' : 'max-age=0',
            # 'referer': urla + '/{}/?page={}&ka=page-{}'.format(cp,page-1,page-1) if page>1 else 'https://www.zhipin.com/c101020100-p100109/',
            'user-agent' : self.agent,
        }

    def get_proxy(self) :
        url = 'http://api.xdaili.cn/xdaili-api//privateProxy/getDynamicIP/DD20203303266CSFaSJ/e13ef122529711e8bcaf7cd30abda612?returnType=1'
        text = requests.get (url).text
        print ('请求代理:', "http://" + text.strip ())
        if '频繁' not in text :
            proxy = {
                'http' : "http://" + text.strip (),
                'https' : 'https://' + text.strip ()
            }
            self.proxy = proxy
        elif '10032' in text :
            print (text)
            print ('代理用完')
            self.proxy = 'None'
        elif '频繁' in text :
            print ('\n5秒后再获取代理\n')
            time.sleep (5.5)
            self.get_proxy ()

    def get_detail(self, jid, lid) :
        url = 'https://www.zhipin.com/view/job/card.json?jid={jid}&lid={lid}&type=2'.format (jid=jid, lid=lid)
        self.agent = random.choice (self.USER_AGENT_LIST)
        self.session.headers.update (self.headers)
        try :
            response = self.session.get (url, proxies=self.proxy, headers=self.headers, timeout=5)
            if '请求成功' in response.text :
                html = response.json () [ 'html' ]
                return html
            elif self.proxy == 'None' :
                return None
            else :
                self.get_proxy ()
                self.get_detail (self, jid, lid)
        except Exception as e :
            print ('\n\n遇到错误', e)
            self.get_proxy ()
            self.get_detail (self, jid, lid)

    def get_one_page_info(self, kw, page) :
        '''获取第page的数据，搜索关键字kw'''
        url = "https://www.zhipin.com/c101020100/?query=" + kw + "&page=" + str (page) + "&ka=page-" + str (page)
        cookies = {
            "lastCity" : "101020100",
            "_uab_collina" : "156594127160811552815566",
            "sid" : "sem_pz_bdpc_dasou_title",
            "__c" : "1566178735",
            "__g" : "sem_pz_bdpc_dasou_title",
            "__l" : "l=%2Fwww.zhipin.com%2F%3Fsid%3Dsem_pz_bdpc_dasou_title&r=https%3A%2F%2Fsp0.baidu.com%2F9q9JcDHa2gU2pMbgoY3K%2Fadrc.php%3Ft%3D06KL00c00fDIFkY0IWPB0KZEgsA_ON-I00000Kd7ZNC00000Irp6hc.THdBULP1doZA80K85yF9pywdpAqVuNqsusK15yRLPH6zuW-9nj04nhRLuhR0IHYYn1mzwW9AwHIawWmdrRN7P1-7fHN7wjK7nRNDfW6Lf6K95gTqFhdWpyfqn1czPjmsPjnYrausThqbpyfqnHm0uHdCIZwsT1CEQLILIz4lpA-spy38mvqVQ1q1pyfqTvNVgLKlgvFbTAPxuA71ULNxIA-YUAR0mLFW5Hfsrj6v%26tpl%3Dtpl_11534_19713_15764%26l%3D1511867677%26attach%3Dlocation%253D%2526linkName%253D%2525E6%2525A0%252587%2525E5%252587%252586%2525E5%2525A4%2525B4%2525E9%252583%2525A8-%2525E6%2525A0%252587%2525E9%2525A2%252598-%2525E4%2525B8%2525BB%2525E6%2525A0%252587%2525E9%2525A2%252598%2526linkText%253DBoss%2525E7%25259B%2525B4%2525E8%252581%252598%2525E2%252580%252594%2525E2%252580%252594%2525E6%252589%2525BE%2525E5%2525B7%2525A5%2525E4%2525BD%25259C%2525EF%2525BC%25258C%2525E6%252588%252591%2525E8%2525A6%252581%2525E8%2525B7%25259F%2525E8%252580%252581%2525E6%25259D%2525BF%2525E8%2525B0%252588%2525EF%2525BC%252581%2526xp%253Did(%252522m3224604348_canvas%252522)%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FH2%25255B1%25255D%25252FA%25255B1%25255D%2526linkType%253D%2526checksum%253D8%26wd%3Dboss%25E7%259B%25B4%25E8%2581%2598%26issp%3D1%26f%3D8%26ie%3Dutf-8%26rqlang%3Dcn%26tn%3Dbaiduhome_pg%26sug%3Dboss%2525E7%25259B%2525B4%2525E8%252581%252598%2525E5%2525AE%252598%2525E7%2525BD%252591%26inputT%3D4829&g=%2Fwww.zhipin.com%2F%3Fsid%3Dsem_pz_bdpc_dasou_title",
            "Hm_lvt_194df3105ad7148dcf2b98a91b5e727a" : "1565941272,1566178735",
            "__zp_stoken__" : "c839%2FbUp4y%2FcG59Q1lQU84czePIXK3dDRi%2F3AGRWQ6KVQWUNKQa4lxpn2jAVyXKDRxk0g3H19loBTLIK4KtUfLuxbQ%3D%3D",
            "__a" : "74852898.1565941271.1565941271.1566178735.32.2.3.3",
            "Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a" : "1566178748",
        }
        headers = {
            "user-agent" : "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
            "referer" : "https://www.zhipin.com/c101020100/?query=python%E5%BC%80%E5%8F%91&page=1&ka=page-1"
        }
        r = requests.get (url, headers=headers, cookies=cookies)
        soup = BeautifulSoup (r.text, "lxml")
        # 先获取每一行的列表数据
        all_jobs = soup.select ("div.job-primary")
        infos = [ ]
        for job in all_jobs :
            jnama = job.find ("div", attrs={"class" : "job-title"}).text
            jurl = "https://www.zhipin.com" + job.find ("div", attrs={"class" : "info-primary"}).h3.a.attrs [ 'href' ]
            jid = job.find ("div", attrs={"class" : "info-primary"}).h3.a.attrs [ 'data-jid' ]
            sal = job.find ("div", attrs={"class" : "info-primary"}).h3.a.span.text
            info_contents = job.find ("div", attrs={"class" : "info-primary"}).p.contents
            addr = info_contents [ 0 ]
            # 有的工作年薪是没有的，有的是有四个的需要更具contents子节点的个数去判断
            # <p>上海 静安区 汶水路<em class="vline"></em>4天/周<em class="vline"></em>6个月<em class="vline"></em>大专</p>
            # contents里面包含着文本和em标签
            # print(info_contents)
            # ['上海 嘉定区 安亭', <em class="vline"></em>, '3-5年', <em class="vline"></em>, '大专']
            if len (info_contents) == 3 :
                work_year = "无数据"
                edu = job.find ("div", attrs={"class" : "info-primary"}).p.contents [ 2 ]
            elif len (info_contents) == 5 :
                work_year = job.find ("div", attrs={"class" : "info-primary"}).p.contents [ 2 ]
                edu = job.find ("div", attrs={"class" : "info-primary"}).p.contents [ 4 ]
            elif len (info_contents) == 7 :
                work_year = job.find ("div", attrs={"class" : "info-primary"}).p.contents [ -3 ]
                edu = job.find ("div", attrs={"class" : "info-primary"}).p.contents [ -1 ]
            company = job.find ("div", attrs={"class" : "company-text"}).h3.a.text
            company_type = job.find ("div", attrs={"class" : "company-text"}).p.contents [ 0 ]
            company_staff = job.find ("div", attrs={"class" : "company-text"}).p.contents [ -1 ]
            print (jid, jnama, jurl, sal, addr, work_year, edu, company, company_type, company_staff)
            infos.append ({
                "jid" : jid,
                "name" : jnama,
                "sal" : sal,
                "addr" : addr,
                "work_year" : work_year,
                "edu" : edu,
                "company" : company,
                "company_type" : company_type,
                "company_staff" : company_staff,
                "url" : jurl})
        print ("%s职位信息，第%d页抓取完成" % (kw, page))
        return infos

    def getpage(self, factor, page) :
        self.agent = random.choice (self.USER_AGENT_LIST)
        self.session.headers.update (self.headers)
        url = 'https://www.zhipin.com/gongsir/{factor}.html?page={page}&ka=page-{page}'.format (factor=factor,
                                                                                                page=page)
        try :
            response = self.session.get (url, proxies=self.proxy, timeout=5, headers=self.headers)
            html = response.text
            if '公司简介' in html :
                print ('----------------获取{}列表页{}page\n'.format (factor, page))
                return html
            elif self.proxy == 'None' :
                return None
            elif '过于频繁' in html or '您的账号安全' in html :
                print ('====过于频繁')
                self.get_proxy ()
                self.getpage (factor, page)
        except :
            self.getpage (factor, page)

    def parse_detail(self, html) :
        ''
        html = etree.HTML (html)
        text = html.xpath ("//div[@class='detail-bottom']//text()")
        text = ''.join ((s.strip () for s in text))
        if len (text) > 20 :
            print ('\t\t解析到详情页', text [ 0 :20 ])
        return text

    def parse_page(self, html) :
        html = etree.HTML (html)
        lis = html.xpath ("//div[@class='job-list']//li")
        for li in lis :
            title = li.xpath (".//h3[@class='name']//div[@class='job-title']//text()") [ 0 ] if len (
                li.xpath (".//h3[@class='name']//div[@class='job-title']//text()")) else None
            salary = li.xpath (".//h3[@class='name']//span[@class='red']//text()") [ 0 ] if len (
                li.xpath (".//h3[@class='name']//span[@class='red']//text()")) else None
            location = li.xpath (".//div[@class='info-primary']/p/text()") [ 0 ] if len (
                li.xpath (".//div[@class='info-primary']/p/text()")) > 0 else None
            require = li.xpath (".//div[@class='info-primary']/p/text()") [ 1 ] if len (
                li.xpath (".//div[@class='info-primary']/p/text()")) > 1 else None
            edu = li.xpath (".//div[@class='info-primary']/p/text()") [ 2 ] if len (
                li.xpath (".//div[@class='info-primary']/p/text()")) > 2 else None
            company = html.xpath ('//div[@class="info-primary"]/h1//text()') [ 0 ] if len (
                html.xpath ('//div[@class="info-primary"]/h1//text()')) else None
            jid = li.xpath ("./a/@data-jid") [ 0 ]
            lid = li.xpath ("./a/@data-lid") [ 0 ]
            url = 'https://www.zhipin.com/' + li.xpath ("./a/@href") [ 0 ] if len (li.xpath ("./a/@href")) else None
            self.num += 1
            print ('\t', self.num, '获得:' + title)
            detail_html = self.get_detail (lid=lid, jid=jid)
            if detail_html :
                infor = self.parse_detail (detail_html)
                with open ('{}boss.txt'.format (company [ :2 ]), 'a', encoding='utf-8', errors='replace') as f1 :
                    f1.write ('\t'.join (
                        str (_) for _ in (title, salary, company, edu, location, require, infor, url)) + '\n')
                item = {
                    'title' : title,
                    'salary' : salary,
                    'location' : location,
                    'require' : require,
                    'edu' : edu,
                    'company' : company,
                    'infor' : infor,
                    'url' : url
                }
                with open ('{}json.txt'.format (company [ :2 ]), 'a', errors='replace', encoding='utf-8') as f2 :
                    f2.write (json.dumps (item, indent=4, ensure_ascii=False) + "\n")
            else :
                pass

    def update_company(self) :
        f = open ('company_url.txt', 'w', encoding='utf-8')
        for page in range (1, 30) :
            r = requests.get ('https://www.zhipin.com/gongsi/?page={page}&ka=page-{page}'.format (page=page),
                              headers=self.headers, proxies=self.proxy)
            html = etree.HTML (r.text)
            if '暂时没有' in r.text :
                break
            elif '过于频繁' in r.text :
                self.proxy = self.get_proxy ()
                self.update_company ()
            elif '精准匹配' in r.text :
                lis = html.xpath ("//div[contains(@class,'company-tab-box') and contains(@class,'company-list')]//li")
                for li in lis :
                    com = li.xpath (".//div[@class='conpany-text']/h4/text()")
                    url = li.xpath (".//div[@class='sub-li']/a[1]/@href")
                    if com and url :
                        com = com [ 0 ]
                        url = url [ 0 ].replace ('/gongsi/', '').replace ('.html', '')
                        self.company [ com ] = url
                        f.write (com + '\t' + url + '\n')
        f.close ()

    def load_company(self) :
        with open ('company_url.txt', 'r', encoding='utf-8') as f :
            companylist = f.readlines ()
            for i in companylist :
                if i :
                    com = i.split ("\t") [ 0 ]
                    url = i.split ("\t") [ 1 ].strip ()
                    self.company [ com ] = url

    def main(self) :
        for key in self.company :
            if self.proxy == 'None' :
                break
            value = self.company [ key ]
            for page in range (1, 31) :
                if self.proxy == 'None' :
                    break
                # html = self.getpage (value, page)
                html = self.get_one_page_info("测试开发", page)
                time.sleep (1)
                if html :
                    self.parse_page (html)


if __name__ == '__main__' :
    boss = BossSpider ()
    boss.main ()
