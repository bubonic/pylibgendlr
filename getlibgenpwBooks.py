#!/usr/bin/env python
#
# TODO: Decode unicode characters in titles and author names from libgen.pw site
# This version has a bibtex info on title page and grabs File Type and MD5 from there
# There is no automatic download and it is redirected to a download page. 


import urllib2
import sys
import unicodedata
import os
import hashlib
import time
import random
import ssl
import httplib
from BeautifulSoup import BeautifulSoup
from socket import error as SocketError



HTTP_PREFIX = 'http://'
URL_ROOT = 'https://libgen.me'
URL_PREFIX = 'https://libgen.me/item/detail/id/'
DL_URL_PREFIX = 'https://libgen.me'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
fCount = 1
pCOUNT = 1
sizeTYPE = ['Kb', 'Mb']
if len(sys.argv) < 4:
    print "Usage: %s /home/user/path/to/id/file /home/user/download/path /home/user/path/to/proxyfile" % sys.argv[0]
    sys.exit()

DLdir=sys.argv[2]
proxyFILE = sys.argv[3]
connected = False
MD5sum = False
cI = 1
bibtexstring = ' '

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile):
        if random.randrange(num + 2): continue
        line = aline
    return line

def change_proxy():
    works = 0
    while works == 0:
        f = open(proxyFILE, 'r')
        proxy = random_line(f)
        f.close()
        proxy = proxy.replace(' ', '')
        proxy = HTTP_PREFIX + proxy
        proxy = proxy.strip()
        sys.stdout.write("Connecting to: ")
        sys.stdout.write(proxy)
        sys.stdout.write("...")
        sys.stdout.flush()
        
        proxyH = urllib2.ProxyHandler({'http': proxy})
        opener = urllib2.build_opener(proxyH)
        opener.addheaders = [('User-agent', USER_AGENT), ('Referer', 'https://tessellations.net')]
        urllib2.install_opener(opener)
        
        try:
            urllib2.urlopen('http://www.google.com', timeout=15)
        except (IOError, httplib.BadStatusLine) as Eproxy:
            sys.stdout.write("Connection error!" + '\n')
            continue
        else:
            sys.stdout.write("Success!" + '\n')
            works = 1    
        sys.stdout.flush()
    return proxy

fname = sys.argv[1]
os.chdir(DLdir)
lastFILE = open('lastfile.txt', 'a+')
oFILE = open('IDs.notfound', 'a')
proxy = change_proxy()
with open(fname) as f:
    IDs = f.readlines()

lastID = lastFILE.readline()

for id in IDs:
    if lastID and id != lastID:
        continue
    lastID = False
    lastFILE.close()
    bookURL = URL_PREFIX + str(id)
    if pCOUNT % 4 == 0:
        proxy = change_proxy()
        
    proxyH = urllib2.ProxyHandler({'http': proxy})
    opener = urllib2.build_opener(proxyH)
    opener.addheaders = [('User-agent', USER_AGENT), ('Referer', 'http://gen.lib.rus.ec/')]
    urllib2.install_opener(opener)
    while not connected and cI < 10:
        try:
            f = urllib2.urlopen(bookURL, timeout=60)
            HTML = f.read()
            print "Retrieved HTML from: %s" % bookURL
            connected = True
            cI = 1
        except (urllib2.HTTPError, ssl.SSLError, urllib2.socket.timeout, urllib2.URLError, SocketError) as Eurl:        
            print "Error opening %s: %s" % (bookURL, repr(Eurl))
            cI += 1
            pass
    if cI == 10:
        print "Download FAILED! Writing ID to IDs.notfound..."
        oFILE.write(id)
        connected = False
        cI = 1
        continue
    cI = 1    
    connected = False
    soup = BeautifulSoup(HTML)
    
    bookTitleBlock = soup.find('div', {'class' : 'book-info__title' })
    bookTitle = bookTitleBlock.getText()
    bookAuthorBlock = soup.find('div', {'class' : 'book-info__lead' })
    bookAuthor = bookAuthorBlock.getText()
    bookDLBlock = soup.find('div', {'class' : 'book-info__download' })
    bookDLaBlock = bookDLBlock.a
    bookDLURL = bookDLaBlock['href']
    bDL = unicodedata.normalize('NFKD', bookDLURL).encode('ascii','ignore')
    bDL = DL_URL_PREFIX + bDL
    BookDLURL = bDL
    bookInfoTable = soup.find("table", {"class" : "book-info__params"})
    #fileTYPE= bookInfoTable.getText().split('File type')[-1]
    #fileSize = bookInfoTable.getText().split('Size')[-1].split("File type")[0]
    
    trData = bookInfoTable.findAll('tr')
    for bibTeXinfo in trData:
        for td in bibTeXinfo.findAll('td'):
            bibtexstring = bibtexstring + td.getText();
 
    fileTYPE = bibtexstring.split('File type:')[-1].split('S')[0]
    fileSize = bibtexstring.split('Size:')[-1].split('W')[0]
    

    print "URL: %s" % bookURL
    print "Title: %s" % bookTitle
    print "Author: %s" % bookAuthor
    print "File Type: %s" % fileTYPE
    print "File Size: %s" % fileSize
    print "Book DL URL: %s" % BookDLURL
    print "Sleeping for 15 seconds...."
    
    time.sleep(15)

    #begin comment for change back to instant dl    
    request = urllib2.Request(BookDLURL)
    request.add_header('User-Agent', USER_AGENT)
    request.add_header('Referer', bookURL.strip()   )    

    proxyH = urllib2.ProxyHandler({'http': proxy})
    opener = urllib2.build_opener(proxyH)
    opener.addheaders = [('User-agent', USER_AGENT), ('Referer', bookURL.strip())]
    urllib2.install_opener(opener)
    bibINFOBLock = soup.find('table', {'class': 'book-info__params'})
    bibINFO = bibINFOBLock.getText()
    for item in bibINFO.split('\n'):
        #if "type" in item:
        #    fileTYPE = item.split('{')[-1]
        #    fileTYPE = fileTYPE.replace('}', '')
        #    fileTYPE = fileTYPE.replace(',', '')
        #    print "File Type: %s" % fileTYPE
        if "MD5" in item:
            MD5sum = item.split('MD5:')[-1].split('SHA')[0]
            #MD5sum = MD5sum.replace('}', '')
            #MD5sum = MD5sum.replace(',', '')
            print "MD5 sum: %s" % MD5sum
            
    #needed for when there is no instant download
    while not connected and cI < 10:
        try:
            f = urllib2.urlopen(BookDLURL, timeout=60)
            HTML = f.read()
            connected = True
            cI = 1
        except (urllib2.HTTPError, ssl.SSLError, urllib2.socket.timeout,  urllib2.URLError, SocketError) as Eurl:        
            print "Error opening %s: %s" % (bookURL, repr(Eurl))
            cI += 1
            pass    
    if cI == 10:
        print "Download FAILED! Writing ID to IDs.notfound..."
        oFILE.write(id)
        connected = False
        cI = 1
        continue
    
    cI = 1
    connected = False
    soup = BeautifulSoup(HTML)
    
    
    bookGetBlock = soup.find('div', {'class' : 'book-info__get'})
    bookGetBlocka = bookGetBlock.a
    bookGetURL = bookGetBlocka['href']


    getBookURL = bookGetURL
    
    print "Get Book URL: %s" % getBookURL
    # end of when there is no instant download
    #print "Bib INFO: %s" % bibINFO
    # begin end of comment for change back 
    # Uncomment when they go back to instant download instead of bibtex page.     
    #getBookURL = BookDLURL
    bookFileName = bookTitle
    bookFileName = unicodedata.normalize('NFKD', bookFileName).encode('ascii','ignore')
    if len(bookFileName) >= 251: 
        bookFileName = bookFileName[0:250]
    bookFileName = bookFileName + "." + fileTYPE
    print "Filename: %s" % bookFileName
    
     
#    print "Sleeping for 15 seconds..."
#    time.sleep(15)
    
#    request = urllib2.Request(getBookURL)
#    request.add_header('User-Agent', USER_AGENT)
#    request.add_header('Referer', BookDLURL.strip())

    proxyH = urllib2.ProxyHandler({'http': proxy})
    opener = urllib2.build_opener(proxyH)
    opener.addheaders = [('User-agent', USER_AGENT), ('Referer', BookDLURL.strip())]
    urllib2.install_opener(opener)

    
    bookFileName = bookFileName.replace('/', '')
    bookFileName = bookFileName.replace('\\', '')
    bookFileName = bookFileName.replace('&#39;', "'")
    try:
        f = urllib2.urlopen(getBookURL, timeout=60)
        if not os.path.isfile(bookFileName): 
            print "Downloading: %s" % bookFileName
            with open(os.path.basename(bookFileName), "wb") as local_file:
                local_file.write(f.read())
        else:
            while os.path.isfile(bookFileName):
                fCount += 1
                bookFileName = bookTitle +  "_" + str(fCount) + "." + fileTYPE
                bookFileName = bookFileName.replace('/', '')
                bookFileName = bookFileName.replace('\\', '')
                bookFileName = bookFileName.replace('&#39;', "'")
            print "Downloading: %s" % bookFileName
            with open(os.path.basename(bookFileName), "wb") as local_file:
                local_file.write(f.read())
                
    except (urllib2.HTTPError, ssl.SSLError, urllib2.socket.timeout, urllib2.URLError, SocketError) as Eurl:
        print "Error: %s" + repr(Eurl)        
        print "Download FAILED! Writing to IDs.notfound..."
        oFILE.write(id)
        continue
    print "Done."
    MD5 = md5(bookFileName)
    print "MD5 sum of file: %s" % MD5
    if MD5sum and str(MD5) == MD5sum:
        print "MD5 sums match!"
    else:
        print "MD5 sums do not match! (or there was no MD5sum in bibinfo)"
    fCount = 1
    dlFILEsize = os.stat(bookFileName).st_size
    if dlFILEsize > 1024:
        dlFILEsize = dlFILEsize / 1024
        sizeType = sizeTYPE[0]; 
        if dlFILEsize > 1024:
            dlFILEsize = dlFILEsize / 1024
            sizeType = sizeTYPE[1]; 
    print "File Size: %s %s" % (dlFILEsize, sizeType)
    print "Sleeping for 42 seconds before retrieving next book...."
    time.sleep(42)
    pCOUNT += 1
    lastFILE = open('lastfile.txt', 'w')
    lastFILE.write(id)
    lastFILE.close()

oFILE.close()
print "Wrote IDs not found to: IDs.notfound"