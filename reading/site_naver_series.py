import os, sys, traceback, json, urllib.parse, requests, argparse, yaml, platform, time, threading, re, base64, fnmatch
import traceback, unicodedata
from datetime import datetime
import urllib.request as py_urllib2
import urllib.parse as py_urllib #urlencode

from lxml import html, etree
import xmltodict

if platform.system() == 'Windows':
    sys.path += ["C:\SJVA3\lib2", "C:\SJVA3\data\custom", "C:\SJVA3_DEV"]
else:
    sys.path += ["/root/SJVA3/lib2", "/root/SJVA3/data/custom", '/root/SJVA3_DEV']

from support.base import get_logger, d, default_headers, SupportFile, SupportString
logger = get_logger()
from urllib.parse import quote
import lxml.html
from lxml import etree
import re
from collections import OrderedDict 



class SiteNaverSeries():
    @classmethod
    def search(cls, title, auth=''):

        url = f"https://series.naver.com/search/search.series?t=all&fs=default&q={quote(title)}"
        logger.error(url)
        text = requests.get(url, headers=default_headers).text
        root = lxml.html.fromstring(text)

        tags = root.xpath('//ul[@class="lst_list"]/li')
        logger.error(tags)
        ret = []

        for tag in tags:
            entity = {}
            entity['code'] = tag.xpath('.//a')[0].attrib['href']
            tmp = None
            logger.debug(d(entity))
            if '/novel/' in entity['code']:
                tmp = 'nov'
            elif '/comic/' in entity['code']:
                tmp = 'com'
            if tmp != None:
                
                entity['title'] = tag.xpath('.//a[@class="N=a:%s.title"]' % tmp)[0].text_content().replace('\n', '').replace('\t', '')
                logger.debug(d(entity))
                entity['author'] = tag.xpath('.//span[@class="author"]')[0].text_content().replace('\n', '').replace('\t', '')
                
                ret.append(entity)
        return ret

    @classmethod
    def info(cls, code):
        try:
            url = f"https://series.naver.com{code}"
            text = requests.get(url, headers=default_headers).text
            root = lxml.html.fromstring(text)

            ret = {}
            tmp = root.xpath('//meta[@property="og:title"]')[0].attrib['content']
            ret['title'] = re.sub("\[.*?\]", '', tmp).strip()
            ret['desc'] = root.xpath('//meta[@property="og:description"]')[0].attrib['content']

            try:
                ret['poster'] = root.xpath('//*[@id="container"]/div[1]/a/img')[0].attrib['src'].split('?')[0]
            except:
                ret['poster'] = root.xpath('//*[@id="container"]/div[1]/span/img')[0].attrib['src'].split('?')[0]

            ret['genre'] = [root.xpath('//*[@id="content"]/ul[1]/li/ul/li[2]/span/a')[0].text_content()]
            ret['author'] = root.xpath('//*[@id="content"]/ul[1]/li/ul/li[3]/a')[0].text_content()
            ret['publisher'] = root.xpath('//*[@id="content"]/ul[1]/li/ul/li[4]/a')[0].text_content()

            if '/novel/' in code:
                url = 'https://series.naver.com/novel/volumeList.series?productNo=' + code.split('productNo=')[1]
            elif '/comic/' in code:
                url = 'https://series.naver.com/comic/volumeList.series?productNo=' + code.split('productNo=')[1]
            
            ret['tag'] = ['네이버시리즈']
            data = requests.get(url, headers=default_headers).json()
            ret['premiered'] = data['resultData'][0]['lastVolumeUpdateDate'].split(' ')[0].replace('-', '')
            return ret
        except Exception as exception:
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
       


if __name__ == '__main__':
    data = SiteNaverSeries.search('낭인전설')
    logger.debug(d(data))
    data = SiteNaverSeries.info(data[0]['code'])
    logger.debug(d(data))



