#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'liuyuantuo@gmail.com'

import requests
import re
import sys

url_head = 'http://flights.ctrip.com'
# 获取到指定的url，然后进行遍历
urls = ["http://flights.ctrip.com/schedule/hrb..html",  # 哈尔滨出发的飞机
        "http://flights.ctrip.com/schedule/.hrb.html"]  # 哈尔滨到达的飞机


def get_fight(url):
    """
        获取到指定的航班信息，返回一个字典组合
        在调用的时候注意进行限速，防止被怀疑为spider
        从这里返回的应该是{flight_no: {start_city: xxx, start_time: xxx, arrive_time: xxx, end_city: xxx}}
        注意，如果有经停的话，经停信息需要打出
        另外，需要进行判断是否有第二页
    """
    #print url
    # 获取到原始的航程
    flight_list = url.split("/")[-1].split(".")
    pattern_next_page = re.compile(r'<a class="schedule_down" href=".*">')


    # 获取到出发城市和到达城市
    start_city = flight_list[0]
    end_city = flight_list[1]
    flight_dict = {}
    ret = requests.get(url)
    page = ret.text
    pattern = re.compile(r'<a href="/schedule/.*target=')
    # 找到所有的飞行表
    flight_urls = pattern.findall(page, re.IGNORECASE)
    # 获取到下一页的地址
    next_page_list = pattern_next_page.search(page)

    if next_page_list is not None:
        next_page_list = next_page_list.group()
        pattern_next_page_detail = re.compile(r'http://.*\.html')
        next_page_url = pattern_next_page_detail.search(next_page_list).group()
    else:
        next_page_url = ""

    pattern = re.compile(r'".*"')
    pattern_time = re.compile(r'<strong class="time">.*</strong>')
    pattern_time_item = re.compile(r'\d{2}:\d{2}')
    for flight_url in flight_urls:
        flight_url = pattern.search(flight_url).group().replace('"', '')
        # 获取到航班号
        flight_no = flight_url.split("/")[2].split(".")[0]
        if not 'cz' in flight_url:
            continue
        # 获取到cz的url
        cz_flight = "{}/{}".format(url_head, flight_url)
        # 打开航班的页面
        origin_page = requests.get(cz_flight)
        page = origin_page.text
        # 获取到时间戳
        origin_time_list = pattern_time.findall(page, re.IGNORECASE)
        if len(origin_time_list) == 0:
            print flight_no, " with no time!"
            continue
        # 获取到起飞时间
        start_time = pattern_time_item.search(origin_time_list[0]).group()
        end_time = pattern_time_item.search(origin_time_list[1]).group()
        flight_dict.setdefault(flight_no,
                               {'start_city': start_city,
                                'end_city': end_city,
                                'start_time': start_time,
                                'end_time': end_time})
    return flight_dict, next_page_url


# 获取到出发的飞机
def get_start(page):
    """
        用于获取在哈尔滨出发的飞机
        1.使用正则匹配到所有飞机的信息
        2.获取到飞机的航班号或者可以查询的信息
    """
    # 进行两次匹配，首先将div里面的内容匹配出来
    pattern = re.compile(r'<a href=.*schedule/hrb\..*</a>')
    href_list = pattern.findall(page, re.IGNORECASE)
    pattern = re.compile(r'".*"')
    url_list = []
    # 获取到url
    for origin_url in href_list:
        url_list.append(pattern.search(origin_url).group().replace('"', ""))
    #print url_list
    return url_list


# 获取到达到的飞机
def get_arrive(page):
    """
        用于获取在回到哈尔滨的飞机
        1.使用正则匹配到所有飞机的信息
        2.获取到飞机的航班号或者可以查询的信息
    """
    # 进行两次匹配，首先将div里面的内容匹配出来
    pattern = re.compile(r'<a href=.*schedule/.*\.hrb.*</a>')
    href_list = pattern.findall(page, re.IGNORECASE)
    pattern = re.compile(r'".*"')
    url_list = []
    # 获取到url
    for origin_url in href_list:
        url_list.append(pattern.search(origin_url).group().replace('"', ""))
    #print url_list
    return url_list

# 获取到航班的起飞时间列表
start_flight_list = []
# 获取到到达的航班时间列表
arrive_flight_list = []

index = 0
# 对url进行遍历，得到我们需要的航班列表
for url in urls:
    index += 1
    print "获取url下的飞机, url: ", url
    ret = requests.get(url)
    # 获取到出发城市为哈尔滨的url
    if index == 1:
        start_url_list = get_start(ret.text)
        start_url_list.remove(url)
        for start_url in start_url_list:
            while "" != start_url and len(start_url) != 0 and len("".join(start_url.split())) != 0:
                # 注意这里可能需要判断是否有第二页，直接加p1即可
                start_flight, start_url = get_fight(start_url)
                if len(start_flight) == 0:
                    break
                start_flight_list.append(start_flight)
    else:
        flight_list = get_arrive(url)
        flight_list.remove(url)
        for arrive_url in flight_list:
            while len("".join(arrive_url.split())) != 0:
                arrive_flight, arrive_url = get_fight(arrive_url)
                if len(arrive_flight) == 0:
                    break
                arrive_flight_list.append(arrive_flight)

print start_flight_list
print arrive_flight_list
sys.exit(0)