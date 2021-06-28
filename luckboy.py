# coding:utf-8
import re
from urllib import request

import requests
from loguru import logger

title = '彩票中奖通知'
SendKey = ''
# 我的投注号码
selectRed = [0, 0, 0, 0, 0, 0]
selectBlue = [0]
timeout = 10


def getHtml(url):
    html = request.urlopen(url)
    return html.read()


# 开奖结果
def getResult():
    # 获取网页html内容
    html = getHtml("http://zx.500.com/ssq/")
    html = html.decode('gb2312')

    # 比对需要的信息
    reg = [r'<dt>([0-9]\d*).*</dt>']  # 期数
    reg.append(r'<li class="redball">([0-9]\d*)</li>')  # 红球
    reg.append(r'<li class="blueball">([0-9]\d*)</li>')  # 蓝球
    reg.append(r'<td class="red money">(.+?)元</td>')  # 奖金

    outstr = ""
    for i in range(len(reg)):
        page = re.compile(reg[i])  # 生成正则
        rs = re.findall(page, html)  # 匹配网页中的正则字符串
        for j in range(len(rs)):  # 获得结果
            outstr += rs[j] + " "

    lot_500_ssq = outstr[:-1].split(' ')
    qh = list(map(int, lot_500_ssq[0:1]))  # 期数
    red = list(map(int, lot_500_ssq[1:7]))  # 红球
    blue = list(map(int, lot_500_ssq[7:8]))  # 蓝球
    redmoney = lot_500_ssq[8:]  # 奖金
    return qh, red, blue, redmoney


# str转bool
def str_to_bool(str):
    return True if str.lower() == 'true' else False


# 查看中奖结果
def lucklyResult(selectRed, selectBlue, qh, red, blue, winnerCondition):
    luckly_red = [item for item in selectRed if item in red]
    luckly_blue = True if blue == selectBlue else False
    for key, value in winnerCondition.items():
        for index in range(len(value['red'])):
            if len(luckly_red) == int(''.join(
                    str(e) for e in value['red']
                    [index:index + 1])) and luckly_blue == str_to_bool(''.join(
                str(e) for e in value['blue'][index:index + 1])):
                return key, value['money'], qh, red, blue


def main():
    url = "http://zx.500.com/ssq/"
    logger.add("logs/luckboy_{time}.log")
    logger.info("--START--")

    qh, red, blue, redmoney = getResult(url)

    # 中奖条件
    oneprize = redmoney[0]  # 一等奖的奖金
    twoprize = redmoney[1]  # 二等奖的奖金

    winnerCondition = {
        '一等奖': {
            'red': [6],
            'blue': [True],
            'money': oneprize
        },
        '二等奖': {
            'red': [6],
            'blue': [False],
            'money': twoprize
        },
        '三等奖': {
            'red': [5],
            'blue': [True],
            'money': '3,000'
        },
        '四等奖': {
            'red': [5, 4],
            'blue': [False, True],
            'money': '200'
        },
        '五等奖': {
            'red': [4, 3],
            'blue': [False, True],
            'money': '10'
        },
        '六等奖': {
            'red': [2, 1, 0],
            'blue': [True, True, True],
            'money': '5'
        },
        '未中奖': {
            'red': [3, 2, 1, 0],
            'blue': [False, False, False, False],
            'money': '0'
        }
    }

    result = lucklyResult(
        selectRed,
        selectBlue,
        qh,
        red,
        blue,
        winnerCondition
    )
    if result:
        content = '期数:{0}\t开奖号码:{1}:{2}'.format(
            result[2], result[3],
            result[4]) + '\t' + '中奖结果:{0}, 每注奖金:{1}元'.format(
            result[0], result[1])

        logger.info(content)

        # 微信通知中奖结果
        zj_jg = result[0]
        if zj_jg != '未中奖':
            payload = {'text': title, 'desp': content}
            url = 'https://sctapi.ftqq.com/{}.send'.format(SendKey)
            requests.post(url, params=payload, timeout=timeout)
    logger.info("--END--")


if __name__ == "__main__":
    main()
