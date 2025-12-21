> 本题返回的地址为合约Voting的地址

Aurora战队进行去中心化民主投票：每个人可以将自己的票权代理给另一人，由他代为执行票权，当支持者人数超过20人即可获得flag！

那么问题来了：你A总人数都没到20人，你怎么拿得到flag啊...

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Voting{
    struct Signature{
        uint8 v;
        bytes32 r;
        bytes32 s;
    }

    mapping(address => uint) public votes;
    string magic_string = "Triode likes to fry his fish, Marin likes to sell his cabbage.";
    uint immutable required = 200; 
    bool solved;

    constructor(address player){
    	// 伪造16个投票者和他们的票权，同时设定玩家票权为10
        for(uint i=0xbeef;i<0xbeff;i++){
            address virtual_voter = address(bytes20(blockhash(i)));
            votes[virtual_voter] = uint160(virtual_voter) % 100;
        }
        votes[player] = 10;
    }

    function get_sig_hash() public view returns(bytes32){
    	// 返回需要进行签名的哈希
        return keccak256(abi.encodePacked(magic_string, uint192(0x0d000721)));
    }

    function solve(Signature[] memory signatures) public{
        uint current_votes = 0;
        for(uint i=0; i<signatures.length; i++) 
        {
            if(i >= 1){
                // 签名不允许被反复利用
                require(keccak256(abi.encode(signatures[i])) != keccak256(abi.encode(signatures[i-1])));
            }
            address voter = ecrecover(get_sig_hash(), signatures[i].v, signatures[i].r, signatures[i].s);
            // 不允许非法签名（ecrecover恢复非法签名不报错，返回0x0地址）
            require(voter != address(0x0), "Invalid signature.");
            current_votes += votes[voter];
        }
        // 大于200票权时本题完成解出
        if(current_votes > required){
            solved = true;
        }
    }

    function isSolved() public view returns(bool){
        return solved;
    }
}
```

