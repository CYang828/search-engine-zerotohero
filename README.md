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

<h3 align="center">search-engine-zerotohero</h3>

  <p align="center">
    从零开始学习企业级搜索引擎的搭建
    <!-- <br />
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>查看文档 »</strong></a>
    <br />
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template">查看例子</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">反馈 Bug</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">提交 Pull Request</a> -->
  </p>
</div>
  <a href="https://github.com/BSlience/search-engine-zerotohero">
    <img src="images/logo.jpg" alt="Logo" width="896" height="541">
  </a>

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

推荐系统在众多应用中都有着举足轻重的地位，不管是短视频应用、电商应用、对话应用、内容搜索应用、社交应用，推荐都是一项必不可少的应用，在给用户提高效率的同时，也能给企业带来不错的收益。但是，市面上很少有成体系的搜索引擎的学习资料，国外的一些资料介绍的技术又相对比较老。这把很多想要学习的小伙伴挡在了门外。鉴于此，我和我的团队开发了这个项目，希望能够填补这块内容的空白，让想要学习搜索的人能够少走弯路的学会这项技术，并且能够把它应用到企业应用中。

如果觉得能够帮助你，请帮忙点一颗星星，非常感谢🙏

<!-- [![Product Name Screen Shot][product-screenshot]](https://github.com/BSlience/search-engine-zerotohero) -->

<p align="right">(<a href="#top">back to top</a>)</p>

### 使用技术

这个部分列举了在本项目中使用的技术和插件。

- [Hadoop](https://hadoop.apache.org/)
- [Spark](https://spark.apache.org/)
- [Hive](https://hive.apache.org/)
- [HBase](https://hbase.apache.org/)
- [Zookeeper](https://zookeeper.apache.org/)
- [Tensorflow](https://www.tensorflow.org/)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->

## 快速开始

快速开始体验搜索引擎搭建过程。

1. 数据导入
   ```bash
   wget -P dataset/ http://xbot.bslience.cn/articles.json.zip
   unzip dataset/articles.json.zip -d dataset/
   # 把数据导入到 mongo中 
   mongoimport -h <host> -d zhihu -c articles --file dataset/articles.json --headerline --type json
   ```
   
<p align="right">(<a href="#top">back to top</a>)</p>

2.
<p align="right">(<a href="#top">back to top</a>)</p>

3. 特征工程建设请移步<a href="https://github.com/BSlience/search-engine-zerotohero/blob/main/featurizer/README.md">featurizer/README.md</a>中启动部分。
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
<!-- ## 如何使用

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#top">back to top</a>)</p> -->

<!-- ROADMAP -->

## 开发地图

也可以查看 [open issues](https://github.com/BSlience/search-engine-zerotohero/issues) 获取关于新特性的更多信息。

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

Project Link: [https://github.com/BSlience/search-engine-zerotohero/](https://github.com/BSlience/search-engine-zerotohero/)

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

[contributors-shield]: https://img.shields.io/github/contributors/BSlience/search-engine-zerotohero.svg?style=for-the-badge
[contributors-url]: https://github.com/BSlience/search-engine-zerotohero/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/BSlience/search-engine-zerotohero.svg?style=for-the-badge
[forks-url]: https://github.com/BSlience/search-engine-zerotohero/network/members
[stars-shield]: https://img.shields.io/github/stars/BSlience/search-engine-zerotohero.svg?style=for-the-badge
[stars-url]: https://github.com/BSlience/search-engine-zerotohero/stargazers
[issues-shield]: https://img.shields.io/github/issues/BSlience/search-engine-zerotohero.svg?style=for-the-badge
[issues-url]: https://github.com/BSlience/search-engine-zerotohero/issues
[license-shield]: https://img.shields.io/github/license/BSlience/search-engine-zerotohero.svg?style=for-the-badge
[license-url]: https://github.com/BSlience/search-engine-zerotohero/blob/master/LICENSE.txt
[product-screenshot]: images/product.jpg
