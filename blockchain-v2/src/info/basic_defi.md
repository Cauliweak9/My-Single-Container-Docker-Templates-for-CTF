#  基础代币框架

众所周知，目前区块链应用最广泛的地方是在金融领域，已经有许多去中心化金融（Decentralized Finance, DeFi）相关的应用了（一般被称为dApps，即Decentralized Apps），这里就介绍两个最基础最简单的代币框架，这两个框架对DeFi生态系统非常重要

##  1. 同质化代币：ERC20

有同学看到标题可能就要问了：同质化代币（Fungible Token）是什么意思呢？其实很简单：如果一种代币和同类型的代币之间是可以任意替换，且价值保持不变，我们就认为这种代币是同质化的，最简单的例子就是我们的法定货币：每张红色毛爷爷价值都是100R，但是每张红色毛爷爷都不一样（毕竟编号放在那里，不可能伪造是吧）

现在我们已经基本了解了同质化代币是怎么样的了，接下来我们就应该进入正题了：以太坊对同质化代币的规范——[ERC-20](https://eips.ethereum.org/EIPS/eip-20)

> 个人推荐看一下官方文档的规范，这是最标准的规范

###  1.1 简易同质化代币——基础功能的实现

让我们从0开始搓一个ERC20代币吧！相信这会使得你对ERC20有进一步的了解的ο(=•ω＜=)ρ⌒☆

作为一个代币，你得有名字，对吧？而且你需要一个英文缩写作为你这个代币的标识，这才能方便别人使用吧，因此我们需要两个函数，其中一个返回名字，另一个返回缩写

这里我们设计一个叫做`Aurora Token`的代币，它的缩写叫`ATK`，因此我们初步有如下的代码：

```solidity
contract Aurora_Token{
	string private _name = "Aurora Token";
	string private _symbol = "ATK";
	
    function name() public view returns (string){
        return _name;
    }

    function symbol() public view returns (string){
        return _symbol;
    }
}
```

我们会发现代币一般都会有小数点的存在，但是我们知道Solidity的数据类型中不存在浮点数，因此我们可以设计一个小数点的位数（比如2），这样如果我们持有404个ATK，最后我们显示的结果就应该是$\frac{404}{10^2}=4.04$，不过一般情况我们设置的位数是18，以对标ether和wei之间的关系

```solidity
function decimals() public view virtual returns (uint8) {
    return 18;
}
```

> 请注意：以上的三个函数都是可选项，因为这些函数都只是为了优化用户体验而设计的，对于代币实际执行的功能影响不大，因此可能会有代币不存在上述三个函数

接下来就到我们代币核心功能的实现了，首先我们需要保证我们的代币不会随意通货膨胀，因此我们需要设置一个函数来返回代币的总供给量，以及一个变量来存放这个供给量：

```solidity
uint256 private _totalSupply;

function totalSupply() public view returns (uint256){
	return _totalSupply;
}
```

> 当然我们可以设计两个函数对代币的总供给量进行中心化调控，即我们的`mint`铸造以及`burn`销毁两个函数：
>

```solidity
/**
 * 这里的_update函数的格式是_update(address from, address to, uint256 value)函数
 * 简单理解为一次转账即可，即from给to转入了value个代币
 */
function _mint(address account, uint256 value) internal {
    if (account == address(0)) {
        revert ERC20InvalidReceiver(address(0));
    }
    _update(address(0), account, value);
}

function _burn(address account, uint256 value) internal {
    if (account == address(0)) {
        revert ERC20InvalidSender(address(0));
    }
    _update(account, address(0), value);
}
```

> 不过这就和我们的去中心化理念相悖了不是吗？而且这两个函数也不在ERC20规范中，但是确实有很多代币是有这两个函数的，因此这里还是稍微提及了一下，但是最后完整的实现不会包含这两个函数

搞定通货膨胀后，接下来是设置一个存放用户余额的变量，以及返回指定用户余额的函数：

```solidity
mapping(address account => uint256) private _balances;

function balanceOf(address _owner) public view returns (uint256 balance){
	return _balances[_owner];
}
```

然后就到了最重要的功能实现——转账功能：

```solidity
function transfer(address _to, uint256 _value) public returns (bool success){
	// 要求转账者余额充足，同时不能转给黑洞地址0x0
	require(_value <= _balances[msg.sender]);
    require(_to != address(0));

    _balances[msg.sender] -= _value;
    _balances[to] += _value;
    return true;
}
```

好的，现在我们已经实现了代币的基础功能了，但是别忘了我们除了EOA地址，还有合约地址，也就是说假如我想要一个合约使用我持有的代币执行某些操作，那我得先转账给这个合约，然后再让这个合约执行一系列操作，这十分的麻烦，而且稍有不注意就会导致代币的丢失（比如我的合约并没有编写代币转回的逻辑，这就会导致我的代币有一部分被固定在了合约中无法被取出，从而造成损失），因此让我们进入到ERC20的核心机制...

###  1.2 ERC20核心机制——allowance机制

我们的ERC20为了解决上一节提到的问题，提出了approve/allowance的机制：即用户A可以对特定的地址B发送许可approve，使得B可以自由地使用A的代币（当然累计总额不能超出指定的许可额度）那么自然需要有一个函数允许用户指定从谁的钱包向谁转出多少代币对吧，因此我们多了一个变量和两个函数（不包括获取allowance的函数）：

```solidity
mapping (address => mapping (address => uint256)) private _allowed;

function allowance(address owner, address spender) public view returns (uint256)
{
	return _allowed[owner][spender];
}

function approve(address spender, uint256 value) public returns (bool) {
    require(spender != address(0));

    _allowed[msg.sender][spender] = value;
    return true;
}

function transferFrom(address from, address to, uint256 value) public returns (bool)
{
    require(value <= _balances[from]);
    require(value <= _allowed[from][msg.sender]);
    require(to != address(0));

    _balances[from] -= value;
    _balances[to] += value;
    _allowed[from][msg.sender] -= value;
    return true;
}
```

那么我们基础的逻辑就完成了，但是我们需要对每一次转账和许可进行通知，为此我们需要两个事件：

```solidity
event Transfer(address indexed _from, address indexed _to, uint256 _value);
event Approval(address indexed _owner, address indexed _spender, uint256 _value);
```

最后经过一些小小的改动使得每次成功的转账都释放事件，我们可以得到这最后的源码：

```solidity
contract Aurora_Token{
	event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);

	string private _name = "Aurora Token";
	string private _symbol = "ATK";
	uint256 private _totalSupply;
	mapping(address account => uint256) private _balances;
	mapping (address => mapping (address => uint256)) private _allowed;
	
    function name() public view returns (string){
        return _name;
    }

    function symbol() public view returns (string){
        return _symbol;
    }
    
    function decimals() public view virtual returns (uint8) {
        return 18;
    }
    
    function totalSupply() public view returns (uint256){
        return _totalSupply;
    }
    
    function balanceOf(address _owner) public view returns (uint256 balance){
        return _balances[_owner];
    }
    
    function transfer(address _to, uint256 _value) public returns (bool success){
        require(_value <= _balances[msg.sender]);
        require(_to != address(0));

        _balances[msg.sender] -= _value;
        _balances[_to] += _value;
        emit Transfer(msg.sender, _to, _value)
        return true;
    }
    
    function allowance(address owner, address spender) public view returns (uint256)
    {
        return _allowed[owner][spender];
    }

    function approve(address spender, uint256 value) public returns (bool) {
        require(spender != address(0));

        _allowed[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }

    function transferFrom(address from, address to, uint256 value) public returns (bool)
    {
        require(value <= _balances[from]);
        require(value <= _allowed[from][msg.sender]);
        require(to != address(0));

        _balances[from] -= value;
        _balances[to] += value;
        _allowed[from][msg.sender] -= value;
        emit Transfer(from, to, value);
        return true;
    }
}
```

至此我们就成功复现了一个ERC20的代币

##  2. 非同质化代币：ERC721

我们已经了解过同质化代币了，那么非同质化代币（Non-Fungible Token, NFT）又是什么呢？根据上面的解释，就是同类型的代币之间价值不尽相同，替换后价值很有可能会发生改变，这不就是我们的数字藏品嘛！（笑）总之我估计看到英文简称很多同学就知道是什么东西了，那我就不再展开了

由于篇幅问题，这里就不再带各位复现一遍ERC721了，一些简单的点各位看规范应该也能看得懂，这里讲一些ERC721和ERC20的区别

###  2.1 safeTransferFrom

相比于ERC20中直接的transferFrom，我们的ERC721标准提出了安全转账safeTransferFrom，同时提出了支持安全转账的合约应用必要的实现，也就是我们的ERC721TokenReceiver接口，里面必须要包含一个`onERC721Received`函数，而对于一个成功的NFT转账，**必定**会返回魔术值`bytes4(keccak256("onERC721Received(address,address,uint256,bytes)"))`，即function selector，对于返回非魔术值的任意情况都**必定**导致交易的回滚，除此之外函数内可以通过override进行修改以满足开发者预期的目的

让我们回到`safeTransferFrom`上，我们发现相比于ERC20，ERC721抛弃了`transfer(address to, uint256 amount)`的public/external函数，而只保留了`transferFrom`和它的安全方法，也就是说ERC721将ERC20中的两个转账函数集成在了同一个函数下

> 如果有敏锐的同学应该能发现我们重入那题的题目代码就是参考了这里的ERC721TokenReceiver

##  2.2 setApprovalForAll

ERC721仍旧保留了approve和相关的机制，但是众所周知，每一个NFT都是独立的，也就是说我们不可能用什么`transferFrom(from, to, amount)`的形式去进行转账，或者使用`approve(to, amount)`这种形式去approve，而是得指定具体的NFT ID进行操作

这个操作看似没有什么太大的问题，但是当NFT持有者持有的NFT很多的时候，如果他想将自己所有的NFT全权代理给另一个人，那就需要多次调用`approve(to, tokenId)`，而这会消耗大量的gas，因此除去`approve`还有另一种`setApprovalForAll`的函数，而这就是用于全权批准的函数：只改变一个状态变量，然后转账的时候检查状态变量的值即可，这能帮助我们节省大量的gas费用

> 对于两种代币详细的实现以及拓展应用可以看OpenZepplin的Github Repo：[OpenZeppelin/openzeppelin-contracts: OpenZeppelin Contracts is a library for secure smart contract development.](https://github.com/OpenZeppelin/openzeppelin-contracts)，在contracts/token下