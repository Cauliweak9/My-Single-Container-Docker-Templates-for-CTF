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
        for(uint i=0xbeef;i<0xbeff;i++){
            address virtual_voter = address(bytes20(blockhash(i)));
            votes[virtual_voter] = uint160(virtual_voter) % 100;
        }
        votes[player] = 10;
    }

    function get_sig_hash() public view returns(bytes32){
        return keccak256(abi.encodePacked(magic_string, uint192(0x0d000721)));
    }

    function solve(Signature[] memory signatures) public{
        uint current_votes = 0;
        for(uint i=0; i<signatures.length; i++) 
        {
            if(i >= 1){
                // Signatures shall not be reused
                require(keccak256(abi.encode(signatures[i])) != keccak256(abi.encode(signatures[i-1])));
            }
            address voter = ecrecover(get_sig_hash(), signatures[i].v, signatures[i].r, signatures[i].s);
            require(voter != address(0x0), "Invalid signature.");
            current_votes += votes[voter];
        }
        if(current_votes > required){
            solved = true;
        }
    }

    function isSolved() public view returns(bool){
        return solved;
    }
}