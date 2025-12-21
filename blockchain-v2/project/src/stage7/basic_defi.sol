// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Aurora_Token{
    event Approval(address indexed approver, address indexed spender, uint amount);
    event Transfer(address indexed from, address indexed to, uint amount);

    mapping(address => uint) Balance;
    mapping(address => mapping(address => uint)) Allowance;
    uint256 public total_supply;

    bool airdrop_received;

    constructor(){
        total_supply = 10_000 ether;
        Balance[address(this)] = 10_000 ether;
    }

    function airdrop() public{
        require(!airdrop_received, "Airdrop received.");
        _approve(address(this), msg.sender, 100 ether);
        airdrop_received = true;
    }

    function balanceOf(address account) public view returns(uint){
        return Balance[account];
    }

    function getAllowance(address approver, address spender) public view returns(uint){
        return Allowance[approver][spender];
    }

    function transfer(address to, uint amount) public{
        _transfer(msg.sender, to, amount);
    }

    function transferFrom(address from, address to, uint amount) public{
        _transfer(from, to, amount);
    }

    function Approve(address spender, uint amount) public{
        _approve(msg.sender, spender, amount);
    }

    function _transfer(address from, address to, uint amount) internal{
        if(from != msg.sender){
            require(getAllowance(from,to) >= amount, "Invalid allowance.");
        }
        require(balanceOf(from) >= amount, "Invalid balance.");
        Balance[from] -= amount;
        Balance[to] += amount;
    }

    function _approve(address approver, address spender, uint amount) internal{
        require(approver != address(0x0) && spender != address(0x0), "Invalid address.");
        Allowance[approver][spender] += amount;
        emit Approval(approver,spender,amount);
    }

    function _burn(uint amount) public{
        require(balanceOf(msg.sender) >= amount, "Invalid balance.");
        Balance[msg.sender] -= amount;
        total_supply -= amount;
    }

    function isSolved(address player) public view returns(bool){
        return balanceOf(player) == total_supply;
    }
}