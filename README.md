# 优雅的收看电视动画

* [订阅视频网站会员](#订阅视频网站会员)
* [硬件准备](#硬件准备)
* [软件配置](#软件配置)
* [订阅RSS](#订阅RSS)
* [自动化下载](#自动化下载)
* [需要做的事](#需要做的事)
* [可选项](#可选项)

## 订阅视频网站会员

找到在当前区域拥有电视动画版权的视频网站，并悉数订阅会员

## 硬件准备

* 支持[Asuswrt-Merlin](https://www.asuswrt-merlin.net/), [OpenWrt](https://openwrt.org/)等开源固件的无线路由器，且至少具备一个USB 3.0接口.
* 硬盘. 建议为2.5英寸, 5400RPM, 容量在1TB以上的的SATA revision 3.0机械磁盘.
* SATA revision 3.0转USB 3.0硬盘盒.
* 或者你也可以一步到位, 使用一张USB 3.0的移动硬盘.

## 软件配置

以下配置均基于我个人所拥有的Asus RT-AC68U无线路由器, 且刷入Asuswrt-Merlin官方固件.

* 根据无线路由器型号[下载](https://www.asuswrt-merlin.net/download)Merlin固件, 在华硕路由器的Web页面刷入. 刷写成功后, 在Web页面勾选`Format JFFS partition at next boot`并再次重启路由器.
* 在Web页面开启路由器的SSH功能, 在电脑上使用SSH工具连接到路由器的Shell.
* 挂载你的硬盘. 需要注意的是，强烈建议将硬盘修改为`EXT4`分区. 可以在路由器的shell中使用`fdisk`命令, 也可以在电脑上使用软件手动分区. 分区会导致硬盘上的所有数据**不可逆的丢失**, 请确保硬盘为空. 使用以下命令检查硬盘的挂载情况
  
    > $ fdisk -l

    ```bash
    Disk /dev/sda: 7739 MB, 7739847680 bytes
    255 heads, 63 sectors/track, 940 cylinders
    Units = cylinders of 16065 * 512 = 8225280 bytes

       Device Boot      Start         End      Blocks  Id System
    /dev/sda1               1         940     7550518+ 83 Linux

    ```

    外置USB分区通常在最后一条

* 配置包管理工具

    安装 Entware-ng , 并选择刚才挂载的分区
  
    > $ entware-setup.sh

    更新 OPKG

    > $ opkg update

    Congratulations! 现在你拥有了一个自由的嵌入式 Linux .

* 配置 transmission

    开源的BitTorrent客户端, 跨平台, 占用资源少.
  
    安装transmission-daemon

    > $ opkg install transmission-daemon-openssl

    安装 transmission-web

    > $ opkg install transmission-web

    停止 transmission-daemon 的服务. 若要修改 transmission 的配置文件, 此步骤为必须.

    > $ /tmp/mnt/sda1/entware/etc/init.d/S88transmission stop

    编辑 transmission-daemon 的配置文件, 位于`/tmp/mnt/sda1/entware/etc/transmission/settings.json` 以下为需要注意的配置项.

    ```json
    {
        "rpc-authentication-required": true, // 开启远程访问密码认证
        "rpc-enabled": true, // 开启远程连接
        "rpc-password": "passwd", // 认证密码
        "rpc-username": "username", // 认证用户名
        "rpc-host-whitelist-enabled": false, // 禁用域名白名单
        "rpc-whitelist-enabled": false, // 禁用IP白名单
        "trash-original-torrent-files": false, // 不自动删除Torrent文件
        "watch-dir": "/opt/etc/transmission/watchdir", // 设置Torrent自动监听目录
        "watch-dir-enabled": true // 开启Torrent自动监听
    }
    ```

    启动 transmission-daemon

    > $ /tmp/mnt/sda1/entware/etc/init.d/S88transmission start

    之后, 访问`http://yourIP:9091`即可登录transmission的Web UI.

* 配置 Python 环境

    安装 python

    > $ opkg install python

    安装 pip

    > $ opkg install python-pip

    安装 python-dev

    > $ opkg install python-dev

    更新 setuptools

    > $ pip install --upgrade setuptools

    更新 pip

    > $ python -m pip install --upgrade pip

    安装 feedparser 组件, 用于解析RSS.

    > $ pip install --upgrade feedparser

* 配置 SMB
  
    在路由器的Web管理页面, 开启SMB服务, 并挂载transmission下载文件夹.

    在你的手机上安装支持SMB协议的视频播放器, 如开源的VLC.

## 订阅RSS

本教程使用的RSS源来自[Mikan Project](https://mikanani.me/). 注册并取得私有的RSS URL.

## 自动化下载

将以下内容保存为`AnimeRSS.py`文件

```python
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
```

将以下内容保存为`config.json`文件

```json
{
    "rss_url" : "rss_url"
}
```

个性化代码和配置文件, 并置入`/tmp/mnt/sda1/entware/etc/transmission/watchdir/`目录中

使用Linux内置的任务调度命令

> crontab -e

按下`a`键，将以下脚本粘贴至窗口内. 这将使系统每间隔6小时执行一次python脚本.

`* */6 * * * cd /tmp/mnt/sda1/entware/etc/transmission/watchdir/ && python AnimeRSS.py`

完成编辑后, 按下`esc`, 键入`:wq`保存并退出编辑.

## 需要做的事

* 在每季度开始时, 订阅感兴趣的动画.
* 在每季度结束时, 清空RSS订阅, 清空Torrent文件, 清空已下载动画.
* 下班回家后拿起手机, 享受动画.

## 可选项

* 配置至少256MB的虚拟内存
* 下载transmission的电脑版作为GUI界面
* 关闭路由器的防火墙, 或配置transmission的出站规则
