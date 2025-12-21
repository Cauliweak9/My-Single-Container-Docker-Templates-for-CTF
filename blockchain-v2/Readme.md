#  Blockchain Docker Template Ver.2

> a.k.a. 千链万花

##  ZH-CN

###  简介

该靶机基于Version 1开发，并在Version 1的基础上进行了轻微的改动，最终作为我们学校内部的新生赛（AuroraCTF 2025）的题目放出，题目的Writeup和一些题外话参考本人博客：[AuroraCTF2025 Misc 部分Writeup | 9C±Void's Blog](https://cauliweak9.github.io/2025/07/04/AuroraCTF2025-Misc-WP/#千链万花)

###  改动与特色

- **改动——环境初始化**：Version 1使用`supervisord`进行多线程任务管理，同时使用固定钱包+随机地址进行环境初始化，经过测试环境初始化时间大约在30秒左右，时间过长；Version 2则模仿了题目合约的部署逻辑，将创建Anvil私链的逻辑统一通过Python的`subprocess`执行，同时通过随机生成助记词创建钱包。
- **改动——前端UI**：让Deepseek V3重新写了一个UI，前后端交互的逻辑基本没有变化，不过添加了若干复制按钮以便于操作。
- **新增——教程页面&题目描述**：由于本系列题目的初心是作为引导题，而目前网上有关区块链的文章知识点较为零散，因此为了节省解题者查询资料的时间，本靶机为每题新增了对应考点的“教程页面”，同时为每题的题目页面添加了题目描述渲染的功能。靶机在读取对应的Markdown文件后使用Python的`markdown`库以及JavaScript的`mathjax`库进行渲染。



##  EN

###  Introduction

This instance is developed based on Version 1, with minor modifications. It was ultimately released as a challenge for our school's internal freshman competition (AuroraCTF 2025). For the writeup and some related information, please refer to my blog: [AuroraCTF2025 Misc 部分Writeup | 9C±Void's Blog](https://cauliweak9.github.io/2025/07/04/AuroraCTF2025-Misc-WP/#千链万花)

###  Modifications and Features

- **Modification—Environment Initialization**: Version 1 uses `supervisord` for multi-threaded task management and uses a fixed wallet + random address for environment initialization. Testing showed that environment initialization took approx. 30 seconds, which is too long. Version 2 mimics the deployment logic of the challenge contract, unifying the creation of the Anvil private chain through Python's `subprocess` function, and creating wallets using randomly generated mnemonic phrases.

- **Modifications—Front-end UI**: A new UI was rewritten using Deepseek V3. The logic of the front-end and back-end interaction remains largely unchanged, but several copy buttons have been added for easier operation.

- **New Features—Tutorial Page & Problem Description**: Since this series of problems was initially intended as introductory questions, and current online articles on blockchain knowledge are scattered, to save solvers' time searching for information, this target machine has added a corresponding "tutorial page" for each problem, and also added a function to render the problem description on each problem's page. The target machine uses Python's `markdown` library and JavaScript's `mathjax` library for rendering after reading the corresponding Markdown file.