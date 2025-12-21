#  拒绝服务攻击（Denial of Service）

各位肯定都听说过DDoS攻击，实际上拒绝服务攻击（DoS）是一种非常常见的攻击手段，总的来说就是通过一系列手段使得服务端无法正常向正常用户提供服务，不管是资源的访问还是其它操作

实际上在Solidity中，我们可以通过Solidity的revert机制实现DoS，这里先介绍一下Solidity的错误机制：

##  0. Solidity错误机制

Solidity中的错误分为2种：`Error(string)`和`Panic(uint256)`，其中前者是被用于常规错误情况，而后者则是用于一个无bug的代码中不应该出现的错误（比如整型溢出）

那么假如确实出现了错误会怎么样呢？Solidity使用状态恢复异常进行错误处理，因此如果出现了错误，这类异常会撤销当前调用以及子调用中对状态所做的所有更改

> 中译中：合约状态不变，但是你会损失用于EVM运行的gas费用

一般的，我们可以使用`assert`和`require`检查状态是否满足，如果不满足则会抛出错误，进而使合约状态revert

> 具体细节的了解请自行阅读[Solidity的官方文档](https://docs.soliditylang.org/en/latest/control-structures.html#error-handling-assert-require-revert-and-exceptions)

##  1. 主动revert

接下来我们设计如下的竞价拍卖的合约：

```solidity
// This code has been slightly modified, original post at https://stackoverflow.com/questions/66099356/a-security-issue-with-requiresend-in-solidity

// INSECURE
contract Auction {
    address currentLeader;
    uint highestBid;

    function bid() payable {
        require(msg.value > highestBid);

        require(currentLeader.send(highestBid)); // Refund the old leader, if it fails then revert
        // currentLeader.transfer(highestBid);

        currentLeader = msg.sender;
        highestBid = msg.value;
    }
}
```

基础逻辑还是很好懂的：出价最高的会成为`currentLeader`，而同时会向上一个Leader返还他之前出的价格，一个非常正常的竞价逻辑

但是有一个问题：这一系列的操作都是基于“用户使用的地址是EOA地址”进行设计的，而如果我们的用户使用的地址是合约地址呢？比如下面的攻击合约：

```solidity
contract Attack{
	constructor(address _Auction) public payable{
		address(_Auction).bid{value: msg.value}();
	}
	
	fallback() external payable{
		revert("Wubba lubba dub dub!");
	}
}
```

> 如果向合约转账，会根据情况调用`fallback() external payable`函数或者`receive()`函数两者之一，两者的差异可以参考[Solidity — Part 2- Payable, Fallback, and Receive | by Shishir Singh | Medium](https://shishirsingh66g.medium.com/solidity-part-2-payable-fallback-and-receive-42c00cb75108)，我们会在重入攻击部分会深入讲解

我们的攻击合约完成竞价后，如果有人尝试压过我们出的价格，那么理论上竞价合约`Auction`会将资金返还给我们的`Attack`合约，但是返还的时候会调用`fallback()`函数，而其中的逻辑是直接`revert`，因此合约的状态会全部回滚，最终导致竞价失败，由此我们可以一直霸占Leader，从而成功以低价格拍得商品

我们在`fallback()`中的`revert`，导致其它正常竞价的人无法正常竞价，这就是Solidity中DoS的一个简单情景

##  2. 通过gas消耗实现revert

众所周知，EVM的运行是基于执行的Opcode消耗gas的（当然除此之外还会有部分gas会发送给矿工作为奖励），而合约作为代码是可能出现无限递归之类的情况的，如果出现这种情况则会消耗大量的区块资源，因此为了防止此类情况发生，以太坊会对每一个区块设置一个可消耗的gas上限，即block gas limit，避免消耗的资源过多

那么我们知道gas消耗是会导致revert的，因此我们可以设置一个无限递归使得gas耗尽从而导致revert，当然这有点费钱就是了（笑），这里就不再举例子了（无限递归应该很好写吧）

> Solidity的有三个转账函数：`transfer`，`send`和`call`，其中除去`call`可以自定义gas，另两个函数在转账过程中只有2300 gas，因此如果是转给合约的话，如果此时合约进行一些正常但是复杂的操作的话，可能会使得gas耗尽，从而导致未预想到的revert
