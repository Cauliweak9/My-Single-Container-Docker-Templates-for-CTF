// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITokenReceiver{
    function onTokenReceived(address operator, address from, address to, uint256 amount, bytes memory data) external returns(bytes4);
}

contract Token {
    event Transfer(address indexed from, address indexed to, uint amount);

    error TokenInvalidReceiver(address receiver);

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
        _transfer(msg.sender, to, amount);
        checkOnTokenReceived(msg.sender, msg.sender, to, amount, data);
    }

    function _transfer(address from, address to, uint amount) internal{
        require(balanceOf(from) >= amount, "Invalid balance.");
        Balance[from] -= amount;
        Balance[to] += amount;
        emit Transfer(from, to, amount);
    }

    function checkOnTokenReceived(address operator, address from, address to, uint256 amount, bytes memory data) internal{
        if (to.code.length > 0){
            try ITokenReceiver(to).onTokenReceived(operator, from, to, amount, data) returns (bytes4 retval){
                if (retval != selector){
                    revert TokenInvalidReceiver(to);
                }
            } catch (bytes memory reason){
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
        require(!airdrop_received, "Airdrop received.");
        token.safeTransfer(msg.sender, 10 ether);
        airdrop_received = true;
    }

    function isSolved() public view returns(bool){
        return token.balanceOf(address(this)) == 0;
    }
}