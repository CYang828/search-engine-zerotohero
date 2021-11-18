## 常用的git提交代码命令
> 日常开发使用的git提交代码的方法

### 一、初始化本地仓库，提交代码，提交到远程git仓库
#### 1、初始化代码仓库
```bash
git init
```
#### 2、将当前目录下的所有文件放到暂存区
```bash
git add .
```
#### 3、查看文件状态
```bash
git status
```
#### 4、添加提交的描述信息
```bash
git commit -m "提交的描述信息"
```
#### 5、远程仓库地址
```bash
git remote add origin "远程仓库地址"
```
### 6、推送到远程仓库
```bash
git push -u origin master
```
---
### 二、创建分支，提交代码到分支
#### 1、创建切换分支
```bash
git checkout -b dev dev为分支名称
git add .
git commit -m '描述'
git push --set-upstream origin dev1 将分支推送到远程仓库
```

#### 2、切换到主分支
```bash
git checkout master
git merge dev 将dev合并到主分支
git push origin master 推送到远程仓库
```
---
### 三、Git实践-Pull Request
- 点击fork就将该项目加入自己的仓库当中
- 本地仓库，远程仓库和分支建立联系
    - clone本地项目
    - 与上游（一开始fork的项目）建立链接
```bash
git remote add upstream https://github.com/QibaiAluminum/EKT.git
git remote -v
```

- 创建分支
```bash
git checkout -b zxr
```
- 提交到自己的仓库
```bash
git add ***  //需要提交的文件
git commit -m "描述" //提交刚才add的说明
git push origin zxr  //将当前分支推送到远程仓库
```
- 申请PR