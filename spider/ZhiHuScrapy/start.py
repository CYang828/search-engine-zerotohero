# @Time    : 2021-11-18 17:58
# @Author  : 老赵
# @File    : start.py.py
import os
import subprocess

## 方法1
# subprocess.check_call('执行的命令', cwd='指定的目录下')

## 方法2
os.system('cd /usr/src/app/ZhiHuScrapy && scrapy crawl zhihu')