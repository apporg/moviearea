# coding=utf8
'''
Created on 2013-2-21

@author: pingqing
'''
import urllib
from BeautifulSoup import BeautifulSoup
import csv
import sys
import json
import md5
import string
import traceback
import time
import csv
import codecs


def subvideoPlayInfo(pageUrl):
    ret = ["",""]
    try:
        time.sleep(0.2)
        htmlSrc = urllib.urlopen(pageUrl).read()
        parser = BeautifulSoup(htmlSrc)
        
        #get the mp4 url
        script =  parser.head.script.contents[0].encode('utf8')
        #print script
        start = script.find('vid:') + len('vid:')
        end = script.find(',', start)
        vid = script[start:end]
        
        start = script.find('mmsid:') + len('mmsid:')
        end = script.find(',', start)
        mmsid = script[start:end]
        ret[0] = "http://m.letv.com/playvideo.php?id=%s&mmsid=%s" % (vid, mmsid)
        
        
        #get the theme 剧情
        ret[1] = "|".join([atag.contents[0].encode('utf8') for atag in parser.body.find('div', 'content').find('div', 'right').find('div', {'id':'cate_info'}).findAll('a')])
    except:
        print "wrong url:", pageUrl
    return ret

def subActors(content):
    actors = []
    for actorLinkTag in content.dl.findAll('dd')[1].findAll('a'):
        actors.append(actorLinkTag.contents[0].encode('utf8'))
    #print actors
    return actors

def subActorsNewVer(content):
    actors = []
    for actorLinkTag in content.dl.findAll('dd')[2].findAll('a'):
        actors.append(actorLinkTag.contents[0].encode('utf8'))
    #print actors
    return actors

def subVideoInfoListVIP(vListPageContent, pageIndex):
    VideoInfoList = []
    vRankInPage = 0
    for content in vListPageContent:
        vRankInPage += 1
        videoInfo = {}
        #print content.div.a.attrs[0][1].encode('utf8')
        
        videoInfo['vDetailUrl'] = "http://yuanxian.letv.com" + content.div.a['href'].encode('utf8')
        
        videoInfo['vid'] =  md5.new(videoInfo['vDetailUrl']).hexdigest()
        
        
        videoInfo['vPlayUrl'] = "http://www.letv.com/ptv/pplay" + content.div.a['href'].encode('utf8').replace("detail/", "")
        #print videoInfo['vPlayUrl']
        
        vplayInfo = subvideoPlayInfo(videoInfo['vPlayUrl'])
        videoInfo['vMp4Url'] = vplayInfo[0]
        videoInfo['vTag'] = vplayInfo[1]
#        if len(videoInfo['vMp4Url']) == 0:
#            continue
        
        videoInfo['vTitle'] = content.div.a['title'].encode('utf8')
        
        #print content.div.a.img.attrs[0][1]
        videoInfo['vImage'] = content.div.a.img['src'].encode('utf8')
        
        
        #print content.dl.dd.a.contents[0]
        videoInfo['vDirector'] = content.dl.dd.a.contents[0].encode('utf8')
        
        #print content.dl.findAll('dd')[1].findAll('a')[1].contents[0]
        videoInfo['vActors'] = subActors(content)
        
        #print content.dl.findAll('dd')[2].contents[1].encode('utf8')
        videoInfo['vPubTime'] = content.dl.findAll('dd')[2].contents[1].encode('utf8')
        
        #print content.dl.findAll('dd')[4].contents[0].encode('utf8')
        videoInfo['vDesc'] = content.dl.findAll('dd')[4].contents[0].encode('utf8').strip()
        
        videoInfo['vRank'] = pageIndex * 100 + vRankInPage
        videoInfo['vCP'] = 'letv'
        videoInfo['vNeedPay'] = '1'
        
        
        #print videoInfo
        if len(videoInfo['vMp4Url']) != 0:
            VideoInfoList.append(videoInfo)
        
        print videoInfo['vid'], videoInfo['vTitle'], videoInfo['vMp4Url']
        #break
        pass
    
    return VideoInfoList


def subVideoInfoListAll(vListPageContent, pageIndex):
    VideoInfoList = []
    vRankInPage = 0
    for content in vListPageContent:
        vRankInPage += 1
        #print content
       
        videoInfo = {}
        #print content.div.a.attrs[0][1].encode('utf8')
        
        videoInfo['vDetailUrl'] = content.a['href'].encode('utf8')
        #print videoInfo['vDetailUrl']
        
        videoInfo['vid'] =  md5.new(videoInfo['vDetailUrl']).hexdigest()
        #print videoInfo['vid']
        
        
        if videoInfo['vDetailUrl'].find('yuanxian.letv.com') == -1:
            videoInfo['vPlayUrl'] = videoInfo['vDetailUrl']
            videoInfo['vNeedPay'] = '0'
        else:
            videoInfo['vPlayUrl'] = videoInfo['vDetailUrl'].replace('yuanxian.letv.com/detail/', 'www.letv.com/ptv/pplay/')
            videoInfo['vNeedPay'] = '1'
        #print videoInfo['vPlayUrl']
        
        
        vplayInfo = subvideoPlayInfo(videoInfo['vPlayUrl'])
        videoInfo['vMp4Url'] = vplayInfo[0]
        videoInfo['vTag'] = vplayInfo[1]
        #print videoInfo['vMp4Url']
        
        videoInfo['vTitle'] = content.dl.find('dd','tit').h1.a.contents[0].encode('utf8')
        #print videoInfo['vTitle']

        videoInfo['vImage'] = content.a.img['src'].encode('utf8')
        #print videoInfo['vImage']
        
        videoInfo['vDirector'] = content.dl.findAll('dd')[1].a.contents[0].encode('utf8')
        #print videoInfo['vDirector']

        videoInfo['vActors'] = subActorsNewVer(content)
        #print videoInfo['vActors']

        videoInfo['vPubTime'] = content.dl.find('dd','year_dl').span.a.contents[0].encode('utf8')
        #print videoInfo['vPubTime']

        videoInfo['vDesc'] = content.dl.find('dd', 'ind24').contents[0].encode('utf8').strip()
        #print videoInfo['vDesc']
        
        videoInfo['vRank'] = pageIndex * 100 + vRankInPage
        videoInfo['vCP'] = 'letv'
        
        #print videoInfo
        if len(videoInfo['vMp4Url']) != 0:
            VideoInfoList.append(videoInfo)
        
        print videoInfo['vid'], videoInfo['vTitle'], videoInfo['vMp4Url']
        #break
        pass
    
    return VideoInfoList

def parsePageByIndexVIP(pageIndex):
    HTMLURL_PATTERN = "http://yuanxian.letv.com/list/search_7_%d_0_1_7_-1_-1_-1_on.html"
    HTMLURL = HTMLURL_PATTERN % (pageIndex,)
    time.sleep(0.2)
    htmlSrc = urllib.urlopen(HTMLURL).read()
    parser = BeautifulSoup(htmlSrc)
    allcontents = parser.body.find('div', {'class':'wrap'}).find('div', {'class':'seekR'}).find('div', {'class':'seekList'}).findAll('div', {'class':'listCont'})
    vlist = subVideoInfoListVIP(allcontents, pageIndex)
    return vlist


def parsePageByIndexALL(pageIndex):
    HTMLURL_PATTERN = "http://so.letv.com/list/c1_t-1_a-1_y-1_f-1_at1_o7_i-1_p%d.html"
    HTMLURL = HTMLURL_PATTERN % (pageIndex,)
    time.sleep(0.2)
    htmlSrc = urllib.urlopen(HTMLURL).read()
    parser = BeautifulSoup(htmlSrc)
    allcontents = parser.body.find('div', 'box_n').find('div', 'main_n').find('div', 'list_r')\
    .find('ol', 'on').find('div', 'soyall').findAll('div', 'info2_box')
    
    vlist = subVideoInfoListAll(allcontents, pageIndex)
    #print allcontents
    return vlist



def quoteString(mystr):
    #return  "".join(["'", mystr.replace("'", "\\'").replace(',', '，').replace("\r", "").replace("\n", ""), "'"]).decode('utf8')
    return mystr.replace("'", "").replace('"', "").replace(',', ' ').replace("\r", "").replace("\n", "").decode('utf8')

def dumpCSV(vlist, fileHandler):
    csvWriter = csv.writer(fileHandle)
    
    
    
    for vitem in vlist:
        tomDumpList = [quoteString(vitem['vid']), \
                       quoteString(vitem['vDetailUrl']), \
                       quoteString(vitem['vPlayUrl']), \
                       quoteString(vitem['vMp4Url']), \
                       quoteString(vitem['vTitle']), \
                       quoteString(vitem['vImage']), \
                       quoteString(vitem['vDirector']), \
                       quoteString("|".join(vitem['vActors'])), \
                       quoteString(vitem['vPubTime']), \
                       quoteString(vitem['vDesc']), 
                       quoteString(str(vitem['vRank'])), \
                       quoteString(vitem['vCP']), \
                       quoteString(vitem['vNeedPay']), \
                       quoteString(vitem['vTag'])]
        
        csvWriter.writerow(tomDumpList)
        pass
    pass


if __name__ == '__main__':
#    print sys.argv[1] the page count to crawler(int)
#    print sys.argv[2] only support csv format
#    print sys.argv[3] the output file name
#    print sys.argv[4] dicide the page url to parse support only vip and all, please check code.
    
    
    fileHandle = codecs.open(sys.argv[3], 'w', 'utf-8')
    
    
    
    #eval('dump'+ string.upper(sys.argv[2]))([])
    pageRange =  range(1, string.atoi(sys.argv[1]) + 1)
    for pageIndex in pageRange:
        print pageIndex
        eval('dump'+ string.upper(sys.argv[2]))(eval("parsePageByIndex" + string.upper(sys.argv[4]))(pageIndex), fileHandle)
        print pageIndex, "done"
    
    fileHandle.close()
    print '============================crawler  done================================================='  
    #print viList