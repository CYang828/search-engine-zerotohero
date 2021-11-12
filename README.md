<div id="top"></div>


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/BSlience/bigdata-zerotohero">
    <img src="images/logo.png" alt="Logo" width="150" height="120">
  </a>

  <h3 align="center">Bigdata-zerotohero</h3>

  <p align="center">
    从零开始学习大数据
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>查看文档 »</strong></a>
    <br />
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template">查看例子</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">反馈 Bug</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">提交 Pull Request</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<!-- <details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details> -->



<!-- ABOUT THE PROJECT -->
## 关于本项目

大数据这个被写进国家重要战略规划的名词，在这些年已经深入人心。有很多人想要学习大数据技术，但是学习这项技术却有着很多天然的屏障：

* 需要很多台电脑组成集群，才能搭建大数据环境。
* 需要配置很多复杂的、不同的组建才能够搭建起来环境。
* 知识体系繁杂，要学的东西太多。
* 不太好直接操作起来，纸面知识过多，没有动手能力。

由于以上这些难点，导致很多对大数据有兴趣的人被挡在了这个非常有趣的领域之外。本项目就是希望，能够通过 docker 技术，给大家提供一个一站式的学习平台，让我们一起分享大数据时代的红利。

[![Product Name Screen Shot][product-screenshot]](https://github.com/BSlience/bigdata-zerotohero)

<p align="right">(<a href="#top">back to top</a>)</p>



### 使用技术

这个部分列举了在本项目中使用的技术和插件。

* [Hadoop](https://hadoop.apache.org/)
* [Spark](https://spark.apache.org/)
* [Hive](https://hive.apache.org/)
* [HBase](https://hbase.apache.org/)
* [Zookeeper](https://zookeeper.apache.org/)
* [Zeppelin](https://zeppelin.apache.org/)
* [Hue](https://docs.gethue.com/quickstart/)
* [Tensorflow](https://www.tensorflow.org/)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->
## 快速开始

快速开始体验大数据环境。

```bash
cd bigdata-environment/
docker-compose up
```

### 步骤1，导入数据到 HDFS 中
```bash
docker cp dataset/ namenode:/hadoop-data/ 

docker exec -it namenode bash
hdfs dfs -mkdir /dataset
hdfs dfs -put /hadoop-data/dataset/* /dataset/
hdfs dfs -ls /dataset
```

### 步骤2，导入数据到 Hive 中 
- 进入 [zeppelin](http://localhost:8085/) 导入 movielens 数据
- 使用 hive 探索 movielens 数据

### 步骤3, Hbase 的使用
- 进入 [zeppelin](http://localhost:8085/) 进入 hbase 教程

### 步骤4，spark 基础
- 进入 [zeppelin](http://localhost:8085/) 进入 spark 教程


<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
<!-- ## 如何使用

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- ROADMAP -->
## 开发地图

- Spark 编程文档更新

也可以查看 [open issues](https://github.com/BSlience/bigdata-zerotohero/issues) 获取关于新特性的更多信息。

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## 如何贡献

贡献可以让社区持续的成长，赋能给更多的人，让人和人、人和项目产生链接。如果你有好的想法，非常欢迎能够加入到开源的团队中。对此，我们**非常感谢**。

如果你有任何建议，能够使本项目变得更好，请 fork 本项目，并且创建一个 pull request。你也可以简单的打开一个 issue，并且打上 "enhancement" 的 tag。不要忘了给本项目一个 star， 再次感谢。

1. 克隆项目
2. 创建你的 Feature 分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的特性 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支上 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## 协议

MIT 协议. 查看 `LICENSE.txt` 获取更多信息。

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTACT -->
## 联系

![](images/wechat.jpg)

知乎 @张春阳 - zhangchunyang_pri@126.com

Project Link: [https://github.com/BSlience/bigdata-zerotohero/](https://github.com/BSlience/bigdata-zerotohero/)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
<!-- ## 你可能会感兴趣

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/BSlience/bigdata-zerotohero.svg?style=for-the-badge
[contributors-url]: https://github.com/BSlience/bigdata-zerotohero/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/BSlience/bigdata-zerotohero.svg?style=for-the-badge
[forks-url]: https://github.com/BSlience/bigdata-zerotohero/network/members
[stars-shield]: https://img.shields.io/github/stars/BSlience/bigdata-zerotohero.svg?style=for-the-badge
[stars-url]: https://github.com/BSlience/bigdata-zerotohero/stargazers
[issues-shield]: https://img.shields.io/github/issues/BSlience/bigdata-zerotohero.svg?style=for-the-badge
[issues-url]: https://github.com/BSlience/bigdata-zerotohero/issues
[license-shield]: https://img.shields.io/github/license/BSlience/bigdata-zerotohero.svg?style=for-the-badge
[license-url]: https://github.com/BSlience/bigdata-zerotohero/blob/master/LICENSE.txt
[product-screenshot]: images/product.jpg






