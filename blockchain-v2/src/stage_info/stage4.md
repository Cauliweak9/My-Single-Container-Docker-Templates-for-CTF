> 本题返回的地址为合约Setup的地址

本题我们设计了2个合约和1个接口规范，其中合约Token为一个自制的虚拟币合约，支持安全转账功能和一个...检查代币是否到账的功能？另一个合约Setup则是本题返回的地址，里面只有一个一次性的空投函数和一个`isSolved`，想要拿到flag？偷走Setup合约的所有Token吧！Persona！（？有小鬼说是）

> 小提示：或许可以从这个奇怪的`onTokenReceived`函数入手？而且好像现实中还有类似的实现？

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITokenReceiver{
    function onTokenReceived(address operator, address from, address to, uint256 amount, bytes memory data) external returns(bytes4);
}

contract Token {
    event Transfer(address indexed from, address indexed to, uint amount);

    error TokenInvalidReceiver(address receiver);

	// 函数选择器，需要这个进行指定函数的调用
    bytes4 selector = bytes4(keccak256("onTokenReceived(address,address,address,uint256,bytes)"));
    mapping(address => uint) Balance;

    constructor(){
        Balance[msg.sender] = 100 ether;
    }

    function balanceOf(address account) public view returns(uint){
        return Balance[account];
    }

    function safeTransfer(address to, uint amount) public{
        safeTransfer(to, amount, "");
    }

    function safeTransfer(address to, uint amount, bytes memory data) public virtual{
    	// 安全转账，支持calldata调用功能以便于智能钱包在接收到代币后进行一系列操作
        _transfer(msg.sender, to, amount);
        checkOnTokenReceived(msg.sender, msg.sender, to, amount, data);
    }

    function _transfer(address from, address to, uint amount) internal{
    	// 实际转账逻辑
        require(balanceOf(from) >= amount, "Invalid balance.");
        Balance[from] -= amount;
        Balance[to] += amount;
        emit Transfer(from, to, amount);
    }

    function checkOnTokenReceived(address operator, address from, address to, uint256 amount, bytes memory data) internal{
    	// 如果代币接收者为合约的话，则会尝试调用该合约的onTokenReceived函数，格式参考上面的interface
        if (to.code.length > 0){
            try ITokenReceiver(to).onTokenReceived(operator, from, to, amount, data) returns (bytes4 retval){
            	// 如果该函数返回值不是函数选择器则revert，并报出非法代币接收者的错误
                if (retval != selector){
                    revert TokenInvalidReceiver(to);
                }
            } catch (bytes memory reason){
            	// 如果函数调用失败，则返回调用失败的错误信息，如无错误信息则返回"Test error"字样
                if (reason.length == 0){
                    revert("Test error");
                } else{
                    assembly ("memory-safe"){
                        revert(add(reason,0x20), mload(reason))
                    }
                }
            } 
        }
    }
}

contract Setup{
    Token public token;
    bool airdrop_received;

    constructor(){
        token = new Token();
    }

    function airdrop() public{
    	// 只能获取一次空投
        require(!airdrop_received, "Airdrop received.");
        token.safeTransfer(msg.sender, 10 ether);
        airdrop_received = true;
    }

    function isSolved() public view returns(bool){
        return token.balanceOf(address(this)) == 0;
    }
}
```

