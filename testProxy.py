#!/usr/bin/python3.6

import random
from urllib.request import build_opener
from urllib.request import ProxyHandler
from urllib.request import install_opener
from urllib.request import urlopen  
import sys
from sys import stdout


HTTP_PREFIX = 'http://'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'


proxyFile = sys.argv[1]

def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile):
        if random.randrange(num + 2): continue
        line = aline
    return line

def change_proxy():
    works = 0
    f = open(proxyFile, 'r')
    while True:
        proxy = f.readline()
        proxy = proxy.replace(' ', '')
        proxy = HTTP_PREFIX + proxy
        proxy = proxy.strip()
        sys.stdout.write("Connecting to: ")
        sys.stdout.write(proxy)
        sys.stdout.write("...")
        sys.stdout.flush()
        
        proxyH = ProxyHandler({'http': proxy})
        opener = build_opener(proxyH)
        opener.addheaders = [('User-agent', USER_AGENT), ('Referer', 'https://tessellations.net')]
        install_opener(opener)
        
        try:
            urlopen('http://www.google.com', timeout=15)
        except IOError:
            sys.stdout.write("Connection error!" + '\n')
            continue
        else:
            sys.stdout.write("Success!" + '\n')
            works = 1    
        sys.stdout.flush()
    return proxy
print("Changing proxy...")
change_proxy()