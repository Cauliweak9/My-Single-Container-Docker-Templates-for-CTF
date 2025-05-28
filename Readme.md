#  My-Single-Container-Docker-Templates-for-CTF

##  Intro  简介

This is a repo where I put my single container (and single exposed port) docker templates for creating CTF challenges, currently I've finished two templates, a Modbus dynamic docker template and a Blockchain dynamic docker template(both of which will work locally without connecting to the Internet, but may not meet your own requirements)

这里放着一些我自己写的给CTF出题的单容器（且单端口暴露）的Docker模板，目前我完成了两个模板，一个是Modbus的动态靶机模板，另一个是区块链的动态靶机模板，两者的正常运行均无需连接至公网，但是可能无法达到您的需求和预期。



Both of the templates uploaded are examples ready to be built and deployed, you may modify all the files to fulfill your requirements and feel free to create issues or contact me directly.

两个模板都是可以直接被搭建并部署的样例，您可以自行修改所有文件以满足您的要求，同时欢迎提Issue或者直接联系我（开盒就不用了www）。

##  Usage  使用

```bash
docker build -t your/tag .
```

Just find where the Dockerfile is at and run the command above.

只需找到Dockerfile所在位置并执行上述代码即可。