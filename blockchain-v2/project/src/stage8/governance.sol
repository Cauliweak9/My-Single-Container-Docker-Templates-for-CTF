// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Governance{
    mapping(address => uint) ownerVotes;
    mapping(address => mapping(address => uint)) public delegatedVotes;
    uint threshold;

    constructor(address player){
        ownerVotes[address(bytes20(blockhash(0x1145141919810)))] = 300;
        ownerVotes[player] = 10;
        threshold = 300;
    }

    function getCurrentVotes(address owner) public view returns(uint){
        return ownerVotes[owner];
    }

    function getThreshold() public view returns(uint){
        return threshold;
    }

    function delegateVotes(address delegator, uint votes) public{
        require(ownerVotes[msg.sender] >= votes, "Invalid votes.");
        delegatedVotes[msg.sender][delegator] += votes;
        ownerVotes[delegator] += votes;
    }

    function undelegateVotes(address delegator, uint votes) public{
        require(delegatedVotes[msg.sender][delegator] >= votes, "Invalid votes.");
        delegatedVotes[msg.sender][delegator] -= votes;
        ownerVotes[delegator] -= votes;
    }
}