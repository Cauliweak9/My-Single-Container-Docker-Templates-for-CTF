双倍返利！免费做慈善！走过路过不要错过哟~

欸，不是，我钱怎么被锁在里面了？——来自一位脑袋尖尖的受害者的发言

> 本题返回的地址为合约Sponsoring的地址

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Sponsoring{
    event Sponsor(address indexed sponsor, uint indexed amount);
    address payable[] public sponsors;
    mapping(address => uint256) public credit_list;

    constructor() payable{
    	// 伪造10个已经投资的用户，无关紧要
        require(msg.value >= 1 ether, "Not enough funds.");
        for (uint i=1337; i<1347; i++) 
        {
            address virtual_sponsor = address(bytes20(blockhash(i)));
            sponsors.push(payable(virtual_sponsor));
            credit_list[virtual_sponsor] = i*2;
        }
    }

    function sponsor() internal{
    	// 无法外部调用的内部函数，添加投资者和资金，并释放事件
        sponsors.push(payable(msg.sender));
        credit_list[msg.sender] = msg.value;
        emit Sponsor(msg.sender, msg.value);
    }

    function payoff() public{
    	// 向投资者双倍返还资金
        uint length = sponsors.length;
        for (uint i=0; i<length; i++) 
        {
            sponsors[i].transfer(credit_list[sponsors[i]]);
            credit_list[sponsors[i]] = 0;
        }
    }

    function isSolved() public returns(bool){
    	// 要求payoff函数调用失败
        (bool success,) = address(this).call(abi.encodeWithSignature("payoff()"));
        if(!success){
            return true;
        }
        return false;
    }

	// 直接向合约转入资金的时候会执行sponsor主逻辑
    fallback() external payable {
        sponsor();
    }

    receive() external payable{
        sponsor();
    }
}
```
