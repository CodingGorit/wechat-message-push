#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import math
import random
import requests

from datetime import date, datetime
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate

today = date.today()

# 微信公众测试号ID和SECRET
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

# 可把os.environ结果替换成字符串在本地调试
user_ids = os.environ["USER_ID"].split(',')
template_ids = os.environ["TEMPLATE_ID"].split(',')
citys = os.environ["CITY"].split(',')
solarys = os.environ["SOLARY"].split(',')
start_dates = os.environ["START_DATE"].split(',')
birthdays = os.environ["BIRTHDAY"].split(',')


# 获取天气和温度
def get_weather(city):
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
    res = requests.get(url).json()
    weather = res['data']['list'][0]
    return weather['weather'], math.floor(weather['temp'])


# 当前城市、日期
def get_city_date(city: str):
    """
    获取城市的当前日期。

    参数:
    city (str): 城市名称。

    返回:
    tuple: (城市名称, 当前日期字符串)。
    """
    if not isinstance(city, str):
        raise TypeError("city must be a string")
    
    try:
        # 使用 datetime.date.today() 获取当前日期
        date_str = today.strftime("%Y-%m-%d")
    except Exception as e:
        raise RuntimeError(f"Error formatting date: {e}")
    
    return city, date_str


# 距离设置的日期过了多少天
def get_count(start_date):
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


# 距离发工资还有多少天
def get_solary(solary_day):
    try:
        # 获取当前年份和月份
        current_year = today.year
        current_month = today.month
        
        # 构建下一次发薪日的日期
        next_solary = date(current_year, current_month, int(solary_day))
        
        # 如果下一次发薪日已经过去，则跳到下一个月
        if next_solary < today:
            if current_month == 12:
                next_solary = date(current_year + 1, 1, int(solary_day))
            else:
                next_solary = date(current_year, current_month + 1, int(solary_day))
        
        return (next_solary - today).days
    except ValueError as e:
        raise ValueError(f"Invalid date format for solary day {solary_day}: {e}")

# 距离过生日还有多少天
def get_birthday(birthday):
    try:
        # 将输入的日期字符串解析为日期对象
        target_date = datetime.strptime(birthday, "%Y-%m-%d").date()
        
        # 计算两个日期之间的差异
        delta = target_date - today
        
        # 返回剩余天数
        return delta.days
    except ValueError as e:
        raise ValueError(f"Invalid date format for target date {birthday}: {e}")


# 每日一句
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


# 字体随机颜色
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

for i in range(len(user_ids)):
    # wea, tem = get_weather(citys[i])
    cit, dat = get_city_date(citys[i])
    data = {
        "date": {"value": "今日日期：{}".format(dat), "color": get_random_color()},
        "city": {"value": "当前城市：{}".format(cit), "color": get_random_color()},
        # "weather": {"value": "今日天气：{}".format(wea), "color": get_random_color()},
        # "temperature": {"value": "当前温度：{}".format(tem), "color": get_random_color()},
        # "love_days": {"value": "今天是你们在一起的第{}天".format(get_count(start_dates[i])), "color": get_random_color()},
        "birthday_left": {"value": "距离她的生日还有{}天".format(get_birthday(birthdays[i])), "color": get_random_color()},
        "solary": {"value": "距离发工资还有{}天".format(get_solary(solarys[i])), "color": get_random_color()},
        "words": {"value": get_words(), "color": get_random_color()}
    }
    if get_birthday(birthdays[i]) == 0:
        data["birthday_left"]['value'] = "今天是她的生日哦，快去一起甜蜜吧"
    if get_solary(solarys[i]) == 0:
        data["solary"]['value'] = "今天发工资啦，快去犒劳一下自己吧"
    res = wm.send_template(user_ids[i], template_ids[i], data)
    print(res) 