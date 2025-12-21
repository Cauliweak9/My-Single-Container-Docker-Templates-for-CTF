// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Sponsoring {
    event Sponsor(address indexed sponsor, uint indexed amount);
    address payable[] public sponsors;
    mapping(address => uint256) public credit_list;

    constructor() payable {
        require(msg.value >= 1 ether, "Not enough funds.");
        for (uint i = 1337; i < 1347; i++) {
            address virtual_sponsor = address(bytes20(blockhash(i)));
            sponsors.push(payable(virtual_sponsor));
            credit_list[virtual_sponsor] = i * 2;
        }
    }

    function sponsor() internal {
        sponsors.push(payable(msg.sender));
        credit_list[msg.sender] = msg.value;
        emit Sponsor(msg.sender, msg.value);
    }

    function payoff() public {
        uint length = sponsors.length;
        for (uint i = 0; i < length; i++) {
            sponsors[i].transfer(credit_list[sponsors[i]]);
            credit_list[sponsors[i]] = 0;
        }
    }

    function isSolved() public returns (bool) {
        (bool success, ) = address(this).call(
            abi.encodeWithSignature("payoff()")
        );
        if (!success) {
            return true;
        }
        return false;
    }

    fallback() external payable {
        sponsor();
    }

    receive() external payable {
        sponsor();
    }
}
