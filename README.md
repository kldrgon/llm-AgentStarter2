# 简易新闻问答
该项目实现了一个极简新闻问答系统
## 初步准备

1. 克隆本仓库到本地

1. 在本项目根目录创建一个 ` .env ` 文件，参考 ` .env.example ` 描述修改内容

## 环境配置

请进入一个具有`python 3.12`的命令行环境

在项目根目录使用命令下载本项目依赖，并创建虚拟环境。

``` bash
python -m pip install poetry
```

使用如下命令创建poetry虚拟环境,并安装依赖。

``` bash
poetry install
```

下载完毕后使用命令，启动服务端。

``` bash
poetry run chainlit run ./src/chat_news_simple/main.py
```

在网页使用即可

## 使用方式

每次新对话的第一句是用来做新闻检索使用的，需要输入自己想检索的内容

在src/chat_news_simple/main.py 的第10行

time_range="d", page=1, max_news=10

time_range        时间范围：h-一个小时内；d-一天内；w-一周内；m-一个月内；年份数字(如2023、2024)-表示限定指定的年份内

page 为起始页码

max_news 是你希望获取的新闻数量