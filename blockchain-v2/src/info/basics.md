#  简陋的入门指引

欢迎！更多的客套话就不说了，让我们直接进入正题吧ヾ(≧▽≦*)o

##  0. 一些可能有用的链接

如果你想了解区块链的基础知识的话，我推荐如下的几个链接：

- [Blockchain Basics | Alchemy Docs](https://www.alchemy.com/docs/blockchain-basics)
- [Learn Blockchain Basics - Cyfrin Updraft](https://updraft.cyfrin.io/courses/blockchain-basics)
- [Web3解释：互联网的未来 | MetaMask Learn](https://learn.metamask.io/zh-CN/lessons/what-is-web3)

当然还有很多其它很好的资源，那就请各位自行探索了

顺带一提，Web3/Blockchain不止有Ethereum一条链，还有Sui链和Solana链之类的其它区块链体系，但是本靶机的题目都是Ethereum链的题目，使用的智能合约语言都是Solidity

想直接上手练习？

- [Ethernaut](https://ethernaut.openzeppelin.com/)
- [Damn Vulnerable DeFi](https://www.damnvulnerabledefi.xyz/)
- [DeFiVulnLabs](https://github.com/SunWeb3Sec/DeFiVulnLabs)



##  1. 环境配置

去中心化钱包得要一个，新手推荐[MetaMask](https://metamask.io/)，非常好搞，而且是浏览器插件的形式，方便快捷

学习Solidity的话肯定需要一个IDE，初学者一般都是使用的[Remix - Ethereum IDE](https://remix.ethereum.org)，用过VSCode的都能很快上手（因为两个都用的Monaco Editor）

开发工具套一般用Hardhat或者Foundry，这个你们自己跟着前面提到的Cyfrin Updraft学习吧，太多了，本出题人懒得写了（笑）



##  2. 初识Solidity

> 如果想学习Solidity，推荐跟着Cyfrin Updraft或者看[Solidity by Example | 0.8.26](https://solidity-by-example.org/)，这里只是放一个最最简单的合约而已

闲话少说，直接上代码：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Hello {
    string hello = "Hello world!";

    function double(uint256 x) public pure returns (uint256){
        return uint256(x*2);
    }

    function greet() public view returns(string memory){
        return hello;
    }
}
```

我们可以看到一个合约就像一个类，和合约交互实际上是和合约内的函数交互，非常友好有没有

简单过一下整个合约：

- `pragma`声明Solidity版本信息，对合约的编译部署至关重要
- `contract`声明合约类名
- `function`声明函数，其中的`public`表示所有地址均可调用
- 合约内可以存放变量，比如`string hello`
- 存在返回值的函数需要预先声明返回值的数据类型

接下来应该就是很正常的函数了，就不再细讲了，至少你现在应该会写一个简单的Hello World了，不是吗？

> 好的我已经不知道写什么了，去Cyfrin Updraft跟着学吧，他们教的太好了

