# coding : utf-8

import requests
from bs4 import BeautifulSoup
import time
import sys
import random
import dns.resolver
import dns.zone
import dns.query
import threading
import re
import os
import argparse
import csv
import json
import ipwhois
from pycountry import countries
from telnetlib import Telnet

try:    # Ugly hack because Python3 decided to rename Queue to queue
    import Queue
except ImportError:
    import queue as Queue

def logo():
    print("""
  _____ _             _        _____      _   
 / ____| |           | |      / ____|    | |  
| (___ | |_ _   _  __| |_   _| |     __ _| |_ 
 \___ \| __| | | |/ _` | | | | |    / _` | __|
 ____) | |_| |_| | (_| | |_| | |___| (_| | |_ 
|_____/ \__|\__,_|\__,_|\__, |\_____\__,_|\__|
                         __/ |                
                        |___/     
                         
            https://www.cnblogs.com/StudyCat/
    
    """)

def get_user_agent() -> str:
    # User-Agents from https://github.com/tamimibrahim17/List-of-user-agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0) chromeframe/10.0.648.205',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_0) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.79 Safari/537.4',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.13) Gecko/20101213 Opera/9.80 (Windows NT 6.1; U; zh-tw) Presto/2.7.62 Version/11.01',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',
        'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; chromeframe/11.0.696.57)',
        'Mozilla/5.0 (Linux; U; Android 2.3; en-us) AppleWebKit/999+ (KHTML, like Gecko) Safari/999.9',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36',
        'Opera/9.80 (X11; Linux i686; U; ja) Presto/2.7.62 Version/11.01',
        'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 1.1.4322)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; ja) Opera 11.00',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24',
        'Opera/9.80 (Windows NT 5.1; U; cs) Presto/2.7.62 Version/11.01',
        'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.17 Safari/537.11',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; InfoPath.1; SV1; .NET CLR 3.8.36217; WOW64; en-US)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5',
        'Mozilla/5.0 (X11; FreeBSD amd64) AppleWebKit/536.5 (KHTML like Gecko) Chrome/19.0.1084.56 Safari/1EA69',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10',
        'Mozilla/5.0 (Linux; U; Android 2.3.5; zh-cn; HTC_IncredibleS_S710e Build/GRJ90) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET CLR 1.1.4322; .NET4.0C; Tablet PC 2.0)',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36',
        'Mozilla/5.0 (X11; CrOS i686 1660.57.0) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.46 Safari/535.19',
        'Mozilla/5.0 (Windows NT 6.1; U; de; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 Opera 11.01',
        'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; Media Center PC 6.0; InfoPath.3; MS-RTC LM 8; Zune 4.7)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/4.0; GTB7.4; InfoPath.3; SV1; .NET CLR 3.1.76908; WOW64; en-US)',
        'Opera/9.80 (X11; Linux x86_64; U; Ubuntu/10.10 (maverick); pl) Presto/2.7.62 Version/11.01',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
        'Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.0; Trident/4.0; FBSMTWB; .NET CLR 2.0.34861; .NET CLR 3.0.3746.3218; .NET CLR 3.5.33652; msn OptimizedIE8;ENUS)',
        'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.9.168 Version/11.51',
        'Opera/9.80 (Windows NT 6.1; U; zh-tw) Presto/2.7.62 Version/11.01',
        'Opera/9.80 (Windows NT 5.1; U; MRA 5.5 (build 02842); ru) Presto/2.7.62 Version/11.00',
        'Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC_Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Opera/9.80 (Windows NT 6.1; U; cs) Presto/2.7.62 Version/11.01',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00',
        'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.3; .NET4.0C; .NET4.0E; .NET CLR 3.5.30729; .NET CLR 3.0.30729; MS-RTC LM 8)',
        'Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.7.62 Version/11.01',
        'Mozilla/5.0 (Windows NT 6.1; U; nl; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 Opera 11.01',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11',
        'Opera/9.80 (Windows NT 6.1; WOW64; U; pt) Presto/2.10.229 Version/11.62',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; Media Center PC 6.0; InfoPath.2; MS-RTC LM 8',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; yie8)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/4.0; InfoPath.2; SV1; .NET CLR 2.0.50727; WOW64)',
        'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.45 Safari/535.19',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.26 Safari/537.11',
        'Opera/9.80 (Windows NT 5.1; U; zh-tw) Presto/2.8.131 Version/11.10',
        'Opera/9.80 (Windows NT 6.1; U; en-US) Presto/2.7.62 Version/11.01',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.0; Trident/4.0; InfoPath.1; SV1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 3.0.04506.30)',
        'Mozilla/5.0 (Linux; U; Android 2.3.4; fr-fr; HTC Desire Build/GRJ22) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Mozilla/5.0 (Windows NT 5.1) Gecko/20100101 Firefox/14.0 Opera/12.0',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3',
        'Opera/9.80 (X11; Linux i686; U; fr) Presto/2.7.62 Version/11.01',
        'Mozilla/4.0 (compatible; MSIE 8.0; X11; Linux x86_64; pl) Opera 11.00',
        'Opera/9.80 (X11; Linux i686; U; hu) Presto/2.9.168 Version/11.50',
        'Opera/9.80 (X11; Linux x86_64; U; bg) Presto/2.8.131 Version/11.10',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
        'Opera/9.80 (X11; Linux i686; U; it) Presto/2.7.62 Version/11.00',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.11 Safari/535.19',
        'Opera/12.0(Windows NT 5.1;U;en)Presto/22.9.168 Version/12.00',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        'Opera/9.80 (X11; Linux i686; U; es-ES) Presto/2.8.131 Version/11.11',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; fr) Opera 11.00',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Zune 4.0; InfoPath.3; MS-RTC LM 8; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.1; SV1; .NET CLR 2.8.52393; WOW64; en-US)',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
        'Opera/9.80 (Windows NT 5.1; U; it) Presto/2.7.62 Version/11.00',
        'Mozilla/5.0 (Linux; U; Android 2.3.3; ko-kr; LG-LU3000 Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Opera/9.80 (Windows NT 6.0; U; pl) Presto/2.7.62 Version/11.01',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3',
        'Opera/9.80 (Windows NT 6.1; U; fi) Presto/2.7.62 Version/11.00',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3',
        'Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02',
        'Mozilla/4.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; pl) Opera 11.00',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)',
        'Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; HTC_DesireS_S510e Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36',
        'Opera/9.80 (Windows NT 6.0; U; pl) Presto/2.10.229 Version/11.62',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)',
        'Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; HTC_DesireS_S510e Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Opera/9.80 (Windows NT 6.1; Opera Tablet/15165; U; en) Presto/2.8.149 Version/11.1',
        'Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00',
        'Opera/9.80 (Windows NT 6.1; U; en-GB) Presto/2.7.62 Version/11.00',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; de) Opera 11.01',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; en) Opera 11.00',
        'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0;  rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3',
        'Opera/9.80 (Windows NT 6.1; U; ko) Presto/2.7.62 Version/11.00',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; Media Center PC 6.0; InfoPath.3; MS-RTC LM 8; Zune 4.7',
        'Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.45 Safari/535.19',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36',
        'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.6.37 Version/11.00',
        'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
        'Mozilla/5.0 (Windows NT 6.0; U; ja; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 Opera 11.00',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; chromeframe/11.0.696.57)',
        'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.8.131 Version/11.11',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; chromeframe/13.0.782.215)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.22 (KHTML, like Gecko) Chrome/19.0.1047.0 Safari/535.22',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; .NET CLR 2.7.58687; SLCC2; Media Center PC 5.0; Zune 3.4; Tablet PC 3.6; InfoPath.3)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
        'Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/5.0 Opera 11.11',
        'Mozilla/5.0 (Macintosh; AMD Mac OS X 10_8_2) AppleWebKit/535.22 (KHTML, like Gecko) Chrome/18.6.872',
        'Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/5.0 (Linux; U; Android 4.0.3; de-ch; HTC Sensation Build/IML74K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.0) yi; AppleWebKit/345667.12221 (KHTML, like Gecko) Chrome/23.0.1271.26 Safari/453667.1221',
        'Mozilla/1.22 (compatible; MSIE 10.0; Windows 3.1)',
        'Opera/9.80 (Windows NT 5.1; U;) Presto/2.7.62 Version/11.01',
        'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
        'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21',
        'Mozilla/5.0 (Linux; U; Android 2.3.5; en-us; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 7.0; InfoPath.3; .NET CLR 3.1.40767; Trident/6.0; en-IN)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F',
        'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.7.62 Version/11.01',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; SLCC1; .NET CLR 1.1.4322)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_5_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.151 Safari/535.19',
        'Opera/9.80 (Windows NT 6.1; U; sv) Presto/2.7.62 Version/11.01',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; Media Center PC 6.0; InfoPath.2; MS-RTC LM 8)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1284.0 Safari/537.13',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5',
        'Opera/9.80 (X11; Linux x86_64; U; fr) Presto/2.9.168 Version/11.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Zune 4.0; Tablet PC 2.0; InfoPath.3; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; chromeframe/12.0.742.112)',
        'Mozilla/4.0 (Compatible; MSIE 8.0; Windows NT 5.2; Trident/6.0)',
        'Opera/12.0(Windows NT 5.2;U;en)Presto/22.9.168 Version/12.00',
        'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
        'Opera/9.80 (X11; Linux x86_64; U; pl) Presto/2.7.62 Version/11.00',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
        'Opera/9.80 (Windows NT 6.0; U; en) Presto/2.8.99 Version/11.10',
        'Opera/9.80 (Windows NT 6.0; U; en) Presto/2.7.39 Version/11.00',
        'Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC_Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari',
        'Mozilla/5.0 (Windows NT 5.1; U; pl; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 Opera 11.00',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; Media Center PC 6.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; de) Opera 11.51',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.6 Safari/537.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.6 Safari/537.11',
        'Opera/9.80 (Windows NT 6.1; U; pl) Presto/2.7.62 Version/11.00',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; Media Center PC 4.0; SLCC1; .NET CLR 3.0.04320)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.45 Safari/535.19',
        'Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/18.6.872.0 Safari/535.2 UNTRUSTED/1.0 3gpp-gba UNTRUSTED/1.0',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36',
        'Opera/9.80 (Windows NT 6.1 x64; U; en) Presto/2.7.62 Version/11.00',
        'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1041.0 Safari/535.21',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/11.10 Chromium/18.0.1025.142 Chrome/18.0.1025.142 Safari/535.19',
        'Mozilla/5.0 (Windows NT 5.1; U; de; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 Opera 11.00'
    ]
    return random.choice(user_agents) 
    
def save2txt(data,filename):
    with open(filename,'w') as f:
        if isinstance(data,str):
            f.write(data+'\n')
        if isinstance(data,list):
            #data = list(set(data))
            data.sort()
            for line in data:
                f.write(line+'\n')  
        if isinstance(data,dict):
            keys = list(data.keys())
            keys.sort()
            for k in keys:
                for line in data[k]:
                    f.write(k+":\n")
                    f.write("    "+line+"\n")

def save2csv(data,filename):
    with open(filename, 'w', newline='',encoding='utf-8-sig') as csvfile:
        fieldnames = ['Hostname', 'IPAddress','Country','ISP','asn_cidr','asn_description','PortScan','StatusCode','httpserver','Title']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(len(data)):
            writer.writerow(data[i])
            
class nslookup():
    def __init__(self,domain):
        self.domain = domain
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 3
        self.resolver.lifetime = 3
        if args.resolver:
            self.resolver.nameservers = args.resolver.split(',')
        else:
            self.resolver.nameservers = ['119.29.29.29','114.114.114.114','8.8.8.8'] 

    def get_mx(self):
        result = []
        try:
            answers = self.resolver.query(self.domain, 'MX')
            for rdata in answers:
                temp = rdata.to_text().rstrip('.')
                mx = temp.split()[1]
                result.append(mx)
            return result    
        except Exception as e:
            return
        
    def get_nameservers(self):
        result = []
        try:
            answers = self.resolver.query(self.domain, 'NS')
            for rdata in answers:
                ns = rdata.to_text().rstrip('.')
                result.append(ns)
            return result    
        except Exception as e:
            print(e)
            return

    def get_soa_rname(self):
        try:
            answers = self.resolver.query(self.domain, 'SOA')
            for rdata in answers:
                soa_rname = rdata.rname.to_text().rstrip('.')
            return soa_rname    
        except Exception as e:
            return
        
    def get_arecord(self):
        result = []
        try:
            answers = self.resolver.query(self.domain, 'A')
            for rdata in answers:
                result.append(rdata.address)
            return result[0]
        except Exception as e:
            return
        
    def get_txt(self):
        result = []
        try:
            answers = self.resolver.query(self.domain, 'TXT')
            for rdata in answers:
                result.append(rdata.to_text())
            return result    
        except Exception as e:
            return
        
    def zone_transfer(self,ns):
        print("Trying zone transfer against %s"%(ns))
        result = []
        try:
            zone = dns.zone.from_xfr(dns.query.xfr(str(ns), domain, relativize=False),relativize=False)           
            names = list(zone.nodes.keys())
            names.sort()
            for n in names:
                result.append(zone[n].to_text(n))    # Print raw zone
            save2txt(result,ns+'_zone.txt') 
            print("Zone transfer sucessful using nameserver %s, and saved to %s\n" %(ns,ns+'_zone.txt'))    
        except Exception as e:
            print("Zone transfer failed")
        
class securitytrails():
    result = {
    'subdomains':[],
    'apexDomains':[],
    'sameIP':{}
    }
    
    def __init__(self):
        self.credential = self.get_credential()
        self.timeout = 10
        
    def get_credential(self):
        url = "https://securitytrails.com/list/ns/ns8.ctrip.com"
        #p = 'csrf_token\s=\s"(.+?)";'
        headers = {'User-Agent':get_user_agent()}
        try:
            r = requests.get(url,headers=headers,timeout=10)
            if r.status_code == 200:
                searchObj = re.search( r'csrf_token = "(.+?)";', r.text, re.M|re.I)
                securitytrails_app = r.cookies['_securitytrails_app']
                if searchObj:
                    csrf_token = searchObj.group(1)
                return {'securitytrails_app':securitytrails_app,'csrf_token':csrf_token}
            else:
                return
        except Exception as e:
            print(e)
            print("securitytrails csrf_token or cookie not found")
            sys.exit(1)

    def parse_records(self,records): 
        hostname = []
        for r in records['records']:
            hostname.append(r['hostname']) 
        return hostname

    def reverse_dns_lookup(self,ns):
        url = f"https://securitytrails.com/app/api/v1/list?ns={ns}"
        headers = {
        'Accept':'application/json',
        'Content-Type':'application/json;charset=utf-8',
        'Referer':'https://securitytrails.com/',
        'User-Agent':get_user_agent()}
        cookies={"_securitytrails_app":self.credential['securitytrails_app']}
        temp = {"_csrf_token":self.credential['csrf_token']}
        csrf_token = json.dumps(temp)

        try:
            r = requests.post(url,headers=headers,cookies=cookies,data = csrf_token,timeout=self.timeout)
            if r.status_code == 200:
                temp = self.parse_records(r.json())
                self.result['apexDomains'].extend(temp)
            else:
                pass
                 
        except Exception as e:
            pass
            
    def reverse_mx_lookup(self,mx):
        url = f"https://securitytrails.com/app/api/v1/list?mx={mx}"
        headers = {
        'Accept':'application/json',
        'Content-Type':'application/json;charset=utf-8',
        'Referer':'https://securitytrails.com/',
        'User-Agent':get_user_agent()}
        cookies={"_securitytrails_app":self.credential['securitytrails_app']}
        temp = {"_csrf_token":self.credential['csrf_token']}
        csrf_token = json.dumps(temp)

        try:
            r = requests.post(url,headers=headers,cookies=cookies,data = csrf_token,timeout=self.timeout)
            if r.status_code == 200:
                temp = self.parse_records(r.json())
                self.result['apexDomains'].extend(temp)
            else:
                pass
        except Exception as e:
            pass
        
    def reverse_soa_lookup(self,soa_rname):
        url = f"https://securitytrails.com/app/api/v1/list?soa_email={soa_rname}"
        headers = {
        'Accept':'application/json',
        'Content-Type':'application/json;charset=utf-8',
        'Referer':'https://securitytrails.com/',
        'User-Agent':get_user_agent()}
        cookies={"_securitytrails_app":self.credential['securitytrails_app']}
        temp = {"_csrf_token":self.credential['csrf_token']}
        csrf_token = json.dumps(temp)

        try:
            r = requests.post(url,headers=headers,cookies=cookies,data = csrf_token,timeout=self.timeout)
            if r.status_code == 200:
                temp = self.parse_records(r.json())
                self.result['apexDomains'].extend(temp)
            else:
                pass
        except Exception as e:
            pass

    def reverse_ip_lookup(self,ip):
        url = f"https://securitytrails.com/app/api/v1/list?ipv4={ip}"
        headers = {
        'Accept':'application/json',
        'Content-Type':'application/json;charset=utf-8',
        'Referer':'https://securitytrails.com/',
        'User-Agent':get_user_agent()}
        cookies={"_securitytrails_app":self.credential['securitytrails_app']}
        temp = {"_csrf_token":self.credential['csrf_token']}
        csrf_token = json.dumps(temp)
        
        try:
            r = requests.post(url,headers=headers,cookies=cookies,data = csrf_token,timeout=self.timeout)
            if r.status_code == 200:
                temp = self.parse_records(r.json())
                if temp:
                    self.result['sameIP'][ip] = []
                    self.result['sameIP'][ip].extend(temp)
                else:
                    self.result['sameIP'][ip] = []
            else:
                pass
        except Exception as e:
            pass
            
    def get_subDomain(self,apexDomain):
        url = f"https://securitytrails.com/app/api/v1/list?apex_domain={apexDomain}"
        headers = {
        'Accept':'application/json',
        'Content-Type':'application/json;charset=utf-8',
        'Referer':'https://securitytrails.com/',
        'User-Agent':get_user_agent()}
        subdomains = []
        cookies={"_securitytrails_app":self.credential['securitytrails_app']}
        temp = {"_csrf_token":self.credential['csrf_token']}
        csrf_token = json.dumps(temp)

        try:
            r = requests.post(url,headers=headers,cookies=cookies,data = csrf_token,timeout=self.timeout)
            if r.status_code == 200:
                result = r.json()
                total_pages = result['meta']['total_pages']
                record_count = result['record_count']
                temp = self.parse_records(result)
                subdomains.extend(temp)
                for page in range(2,total_pages+1):
                    url = f"https://securitytrails.com/app/api/v1/list?apex_domain={apexDomain}" + "&page=" + str(page)
                    r = requests.post(url,headers=headers,cookies=cookies,data = csrf_token,timeout=self.timeout)
                    temp = self.parse_records(r.json())
                    subdomains.extend(temp)

                self.result['subdomains'].extend(subdomains) 
            else:
                pass
        except Exception as e:
            pass
        
    def Find_associated_domains(self,domain,dns):
        modules = ['dns','mx','soa']

        if 'dns' in modules:            
            nameservers = dns.get_nameservers()
            if nameservers:
                for ns in nameservers:
                    if ns.find(domain) != -1:
                        self.reverse_dns_lookup(ns)
        if 'mx' in modules:
            MX_records = dns.get_mx()            
            if MX_records:
                for mx in MX_records:
                    if mx.find(domain) != -1:
                        self.reverse_mx_lookup(mx)        
        if 'soa' in modules:
            soa_rname = dns.get_soa_rname()
            if soa_rname and soa_rname.find(domain) != -1:
                self.reverse_soa_lookup(soa_rname)    
        self.result['apexDomains'] =  list(set(self.result['apexDomains']))   

class subDomainBatch(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        
    def search_subDomain(self,domain):
        if sys.stdout.isatty():     # Don't spam output if redirected
            sys.stdout.write("Finding subdomains for "+ domain + "                              \r")
            sys.stdout.flush()
        st.get_subDomain(domain)
        
    def run(self):
        while True:
            try:
                domain = self.queue.get(timeout=1)
            except Exception as e:
                return
            self.search_subDomain(domain)
            self.queue.task_done()

class scanner(threading.Thread):
    def __init__(self, queue,ports,dns):
        global domainInfo
        threading.Thread.__init__(self)
        self.queue = queue
        self.ports = ports    
        self.dns = dns

    def get_ipinfo(self, domain):
            try:
                if sys.stdout.isatty():     # Don't spam output if redirected
                    sys.stdout.write(domain + "                              \r")
                    sys.stdout.flush()
               
                IPAddress = self.dns.get_arecord()
                if not IPAddress:
                    print("None of DNS query names exist: %s"%(domain))
                else:
                    httpinfo = HTTPHeaders(domain)
                    if httpinfo:
                        title = httpinfo['title']
                        status_code = httpinfo['status_code']
                        httpserver = httpinfo['httpserver']
                    else:    
                        title = ""
                        status_code = ""
                        httpserver = ""                      
                    ipinfo = do_ipwhois(IPAddress)
                    msg = ""
                    for port in self.ports:
                        if do_telnet(IPAddress,port):
                            msg = msg + port+"|"
                    if msg:
                        msg = msg[:-1]+"(open)" 
                    res = {'Hostname':domain,'IPAddress':IPAddress,'ISP':ipinfo['isp'],'Country':ipinfo['country'],'asn_cidr':ipinfo['asn_cidr'],'asn_description':ipinfo['asn_description'],'PortScan':msg,'StatusCode':status_code,'httpserver':httpserver,'Title':title} 
                    domainInfo.append(res)    
            except Exception as e:
                print(e)

    def run(self):
        while True:
            try:
                domain = self.queue.get(timeout=1)
            except Exception as e:
                return
            self.get_ipinfo(domain)
            self.queue.task_done()
            
def do_ipwhois(IPAddress):
    try:
        info = ipwhois.IPWhois(IPAddress).lookup_whois()
    except Exception as e:
        return {'country':'Unknown','isp':'Unknown','asn_cidr':'Private-Use Networks','asn_description':'Private-Use Networks'}

    city = (info['nets'][0]['city']  if(info['nets'][0]['city']) else "")     
    country = countries.get(alpha_2=info['nets'][0]['country'])
    if city:
        countryname = country.name +'/'+city
    else:
        countryname = country.name
    if info['nets'][0]['description']:
        temp = info['nets'][0]['description'].splitlines()
        ipinfo = {'country':countryname,'isp':temp[0],'asn_cidr':info['asn_cidr'],'asn_description':info['asn_description']}
    else:
        ipinfo = {'country':countryname,'isp':'Not Found','asn_cidr':info['asn_cidr'],'asn_description':info['asn_description']}
    return ipinfo
                      
def do_zonetransfer():
    print("Getting nameservers")
    nameservers = dns.get_nameservers()
    if nameservers:
        for ns in nameservers:
            print("Trying zone transfer against " + str(ns))
            dns.zone_transfer(ns) 

def get_subDomain_batch(apexDomains):
    queue = Queue.Queue()
    for domain in apexDomains:
        queue.put(domain)
        
    threads = args.threads
    threads_list = []   
    try:
        for i in range(threads):
            t = subDomainBatch(queue)
            t.setDaemon(True)
            threads_list.append(t)
        
        for i in range(threads):
            threads_list[i].start()
        
        for i in range(threads):
            threads_list[i].join(1024)        
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, quitting...")
        sys.exit(1)        
  
def HTTPHeaders(domain):
    url = 'http://'+domain.strip()
    url2 = 'https://'+domain.strip()
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36'}
    try:
        r = requests.get(url,headers=headers,allow_redirects=True,timeout=8)
    except Exception as e:
        try:
            r = requests.get(url2,headers=headers,allow_redirects=True,timeout=8)
        except Exception as e:
            return

    try:
        status_code = str(r.status_code) + ' ' + requests.status_codes._codes[r.status_code][0]
        if "server" in r.headers.keys():
            server = r.headers["server"]
        else:
            server = ""
        if requests.utils.get_encodings_from_content(r.text):
            coding = requests.utils.get_encodings_from_content(r.text)[0]
        else:
            coding = 'utf-8'
        if r.encoding:
            html = r.text.encode(r.encoding,"ignore").decode(coding,"ignore")
        else:
            html = r.text
        soup = BeautifulSoup(html, "html.parser")
        if soup.title:
            title = soup.title.string
        else:
            title = ""
        return {"title":title,"status_code":status_code,"httpserver":server} 
    except Exception as e:
        return 

def do_telnet(ip,port):
    server = Telnet()
    try:
        server.open(ip,port,timeout=4)
        return True
    except Exception as e:
        return False
    finally:
        server.close() 

def do_whois(all_subdomains):
    global domainInfo
    domainInfo = []
    queue = Queue.Queue()
    for domain in all_subdomains:
        queue.put(domain)

    ports = args.ports.split(',')
    threads = args.threads
    threads_list = []    
    try:
        for i in range(threads):
            t = scanner(queue,ports,dns)
            t.setDaemon(True)
            threads_list.append(t)
        
        for i in range(threads):
            threads_list[i].start()
        
        for i in range(threads):
            threads_list[i].join(1024)        
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, quitting...")
        sys.exit(1)
        
    time.sleep(1)    
    try:        
        save2csv(domainInfo,output_filename)
        print("The scan result has been saved to %s\n" % (output_filename)) 
    except Exception as e:
        print(e)        
        
def get_args():
    global args
    
    parser = argparse.ArgumentParser( formatter_class=lambda prog:argparse.HelpFormatter(prog,max_help_position=40))
    parser.add_argument('-d', '--domain', help='Target domain', dest='domain', required=True)
    parser.add_argument('-p', '--port', help='Ports to scan, default 80,443', dest='ports', required=False,default="80,443")
    parser.add_argument('-t', '--threads', help='Number of threads,default 8', dest='threads', required=False, type=int, default=8)
    parser.add_argument('-o', '--output', help="Write output to a csv file", dest='output', required=False)
    parser.add_argument('-R', '--resolver', help="Use the specified resolver instead of the system default", dest='resolver', required=False)
    parser.add_argument('-n', '--only', action="store_true", default=False, help='Finding associated domains only', dest='only', required=False)
    args = parser.parse_args()

def main(): 
    starttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    global dns,st,output_filename
    output_sub = args.domain + "_sub.txt"
    output_apex = args.domain + "_apex.txt"
    if not args.output:
        output_filename = args.domain + "_output.csv"
    else:
        output_filename = args.output
    dns = nslookup(args.domain)
    ip = dns.get_arecord()
    apexDomains = []
    nameservers = dns.get_nameservers()

    ipinfo = do_ipwhois(ip)
    print("Doing nslookup\nTarget: %s\nIPAddressess: %s"%(args.domain,ip))
    print("Country: %s    ISP: %s    ASN: %s\n" % (ipinfo['country'],ipinfo['isp'],ipinfo['asn_description']))
    for ns in nameservers:
        dns.zone_transfer(ns)
    
    print("\nFinding associated domains")
    st = securitytrails()
    if os.path.exists(output_apex):
        with open(output_apex,'r') as file:
            apexDomains = file.read().splitlines()
    else:               
        st.Find_associated_domains(args.domain,dns)
        apexDomains = st.result['apexDomains']
        apexDomains.append(args.domain)
        
    if apexDomains:
        apexDomains = list(set(apexDomains))
        save2txt(apexDomains,output_apex)
        print("%d associated domains found for %s, and saved to %s\n"%(len(apexDomains),args.domain,output_apex))
    
    print("Finding subdomains for every associated domain")  
    if os.path.exists(output_sub):
        with open(output_sub,'r') as file:
            all_subdomains = file.read().splitlines()  
    else:   
        get_subDomain_batch(apexDomains) 
        if st.result['subdomains'] :
            all_subdomains = list(set(st.result['subdomains']))
            
    save2txt(all_subdomains,output_sub)
    print("%d subdomains found, and saved to %s\n"%(len(all_subdomains),output_sub))
    
    if not args.only:
        print("Geting information for domains")
        do_whois(all_subdomains)    
    print ("Start at %s \nEnd   at %s" %(starttime,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))     
if __name__ == "__main__":
    logo()
    get_args()
    main()  
