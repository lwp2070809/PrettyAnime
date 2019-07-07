#coding=utf-8
import os
import feedparser
import urllib2
import json

# 从配置文件中读取RSS订阅链接
with open("config.json") as f:
    config = json.load(f)
rss_url = config["rss_url"]  
rss_content = feedparser.parse(rss_url)
for i in range(len(rss_content.entries)) :
    # 不同RSS站点的解析方式也不同
    torrent_url =  rss_content.entries[i].links[2].href  
    # 取得Torrent文件名
    torrent_file =  torrent_url.rsplit('/')[-1]  
    # 若Torrent文件已存在则跳过
    if os.path.isfile(torrent_file + ".added") :  
        continue
    # 网站反爬虫，故设置header模拟浏览器访问
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    request = urllib2.Request(url=torrent_url,headers=headers)  
    data = urllib2.urlopen(request)
    # 保存Torrent文件
    with open(torrent_file, 'wb') as f :
        f.write(data.read())
