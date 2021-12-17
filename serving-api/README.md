# 使用FastAPI搭建远程API接口
---
## 一、app代码结构
参考：https://github.com/nsidnev/fastapi-realworld-example-app
```python
app
├── api              - web related stuff.
│   ├── dependencies - dependencies for routes definition.
│   ├── errors       - definition of error handlers.
│   └── routes       - web routes.
├── core             - application configuration, startup events, logging.
├── db               - db related stuff.
│   ├── migrations   - manually written alembic migrations.
│   └── repositories - all crud stuff.
├── models           - pydantic models for this application.
│   ├── domain       - main models that are used almost everywhere.
│   └── schemas      - schemas for using in web routes.
├── resources        - strings that are used in web responses.
├── services         - logic that is not just crud related.
└── main.py          - FastAPI application creation and configuration.
```
## 二、FastAPI介绍
　FastAPI 是用于构建 Web API 的现代、开源、快速、高性能的 Web 框架，它基于Python 3.6+ 标准类型提示，支持异步，正如它的名字，FastAPI 就是为构建快速的 API 而生。
### 2.1 优点

自动类型检查。这意味着更少的 Bug，即使在深度嵌套的 JSON 请求中，Fast API 也会验证开发人员的数据类型。
集众所长，站在巨人的肩膀上。FastAPI 建立在 JSON Schema（用于验证JSON数据结构的工具），OAuth 2.0（用于授权的行业标准协议）和OpenAPI（这是可公开获得的应用程序编程接口）之类的标准之上。
现代化。FastAPI 使使用称为 graphene-python 的 Python 库轻松构建 GraphQL API 。
快速、高性能。可以和 NodeJS 和 Go 相提并论。
### 2.2 缺点

由于 FastAPI 相对较新，因此与其他框架相比，社区较小，第三方的教程相对较少。
### 2.3 用例

FastAPI 适用于构建高性能的 API，本身支持异步，如果要构建异步 API，可以优先选择 FastAPI。Netflix 将其用于内部危机管理。它还可以在部署准备就绪的机器学习模型时完美缩放，因为当 ML 模型封装在 REST API 并部署在微服务中时，它在生产中会发挥最佳作用。

## 三、代码编写
