# -*- coding: utf-8 -*-
import os
import time
import random
import json
from lxml import etree
import psutil
import redis
import requests
import telnetlib
import threading
from my_fake_useragent import UserAgent
# import sys
# import platform
#
# if (platform.system() == 'Windows'):
#     sys.path.append('../')
# elif (platform.system() == 'Linux'):
#     sys.path.append('/home/ec2-user/python')
# else:
#     print('不支持该系统，请更新代码......')
# from bill_crawler.config.db_cofig import *
# from bill_crawler.alarm.alarm_email import e_mail
# from bill_crawler.data.redis_data import *


# ip代理池
class IpPool:
    def __init__(self):
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random()
        }
        # ip代理API
        self.ipurl = 'http://http.tiqu.qingjuhe.cn/getip?num=1&type=2&pack=51811&port=11&lb=1&pb=4&regions='
        # redis数据库
        self.redi = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True, password='hch123456')
        # 接口请求失败计数
        self.count = 0

    # 获取代理ip
    def get_ip(self):
        try:
            res = requests.get(url=self.ipurl, headers=self.headers, timeout=10)
            print(res.status_code)
            print('获取时间：{}'.format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))))), res.text)
            if res.status_code != 200:
                self.count += 1
            else:
                self.count -= 1
            # 接口返回数据
            # {"code":0,"data":[{"ip":"223.241.61.18","port":"4336"}],"msg":"0","success":true}
            json_obj = res.json()
            if res.status_code == 200 and json_obj['data'][0]:
                if self.proxyip(json_obj['data'][0]['ip']):
                    return json_obj['data'][0]
                    # return {'ip': '127.0.0.1', 'port': '1234'}
        except:
            self.count += 1

    # 存储ip
    def set_ip(self, ip):
        print('存入：', ip)
        self.redi.lpush('ip:iplist', json.dumps(ip))

    # 检测IP有效性
    def test_ip(self, item):
        item = json.loads(item)
        try:
            telnetlib.Telnet(item['ip'], port=item['port'], timeout=10)
        except:
            return False
        else:
            return True

    def proxyip(self, ip):
        url = 'https://iphunter.net/ip/{}'.format(ip)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        }
        res = requests.get(url, headers=headers)
        e = etree.HTML(res.text)
        data = ''.join(e.xpath('/html/body/article/script[3]/text()'))
        if '代理' not in data and '爬虫' not in data:
            return True
        else:
            return False

    # 引擎
    def engine(self):
        while True:
            if self.redi.llen('ip:iplist') >= 19:
                for item in self.redi.lrange('ip:iplist', 0, -1):
                    print('检测时间：{}'.format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))))), item)
                    if item == None:
                        print(None)
                        # 清除无效IP
                        self.redi.lrem('ip:iplist', 1, item)
                        # # 补充有效IP
                        time.sleep(2)
                        ip = self.get_ip()
                        if ip:
                            self.set_ip(ip)
                    if not self.test_ip(item):
                        print(self.test_ip(item))
                        # 清除无效IP
                        self.redi.lrem('ip:iplist', 1, item)
                        # # 补充有效IP
                        time.sleep(2)
                        ip = self.get_ip()
                        if ip:
                            self.set_ip(ip)
            else:
                for i in range(20):
                    time.sleep(2)
                    if self.redi.llen('ip:iplist') <= 20:
                        print('ip数量小于20')
                        ip = self.get_ip()
                        if ip:
                           self.set_ip(ip)
            time.sleep(30)

    # 客户端随机ip
    def random_ip(self):
        try:
            iplist = self.redi.lrange('ip:iplist', 0, -1)
        except:
            iplist = []
        if iplist:
            while True:
                ip = random.choice(iplist)
                if ip:
                    ip = json.loads(ip)
                    # ip_info = '183.166.164.209:4370'
                    ip_info = ip['ip'] + ':' + ip['port']
                    proxies = {'https': ip_info}
                    return ip_info
                    # proxies = {'https': '119.5.74.242:4385'}
        else:
            return None

    # 运行
    def run(self):
        pid = str(os.getpid())
        self.redi.set('pid:ip_pool', pid)
        self.engine()

if __name__ == '__main__':
    ippool = IpPool()
    pid = ippool.redi.get('pid:ip_pool')
    if pid:
        status = psutil.pid_exists(int(pid))
        if not status:
            # 启动
            ippool.run()
    else:
        # 启动
        ippool.run()

