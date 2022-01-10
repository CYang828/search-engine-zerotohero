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

### 常见git命令
- 初始化一个Git仓库 git init
- 查看分支：git branch
- 创建分支：git branch <name>
- 切换分支：git checkout <name>
- 创建+切换分支：git checkout -b <name>
- 合并某分支到当前分支：git merge <name>
- 删除分支：git branch -d <name>
- 新建一个标签 git tag <name>
- 指定标签信息 git tag -a <tagname> -m "blablabla..."
- 用PGP签名标签 git tag -s <tagname> -m "blablabla..."
- 查看所有标签 git tag
- 推送一个本地标签 git push origin <tagname>
- 推送全部未推送过的本地标签 git push origin --tags
- 删除一个本地标签 git tag -d <tagname>
- 删除一个远程标签 git push origin :refs/tags/<tagname>
- 查看远程库信息 git remote -v；
- 从本地推送分支 git push origin branch-name，如果推送失败，先用git pull抓取远程的新提交；
- 在本地创建和远程分支对应的分支 git checkout -b branch-name origin/branch-name，本地和远程分支的名称最好一致；
- 建立本地分支和远程分支的关联 git branch --set-upstream branch-name origin/branch-name；
- 从远程抓取分支 git pull，如果有冲突，要先处理冲突。
- 工作区的状态 git status命
- 查看修改内容 git diff
- 版本回滚 git reset --hard commit_id
- 查看提交历史 git log 查看命令历史 git reflog


### fork更新
步骤总结
1. bash进入项目目录
2. git remote add upstream 上游仓库名称.git
3. git checkout master
4. git fetch upstream
5. git merge upstream/master
6. git push origin master
- https://blog.csdn.net/formemorywithyou/article/details/97311556
- https://blog.csdn.net/qq1332479771/article/details/56087333