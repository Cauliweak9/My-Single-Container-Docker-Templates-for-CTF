// SPDX-License-Identifier: MIT
pragma solidity 0.8.30;

contract Example {
    bool solved;

    function solveChallenge() public{
        solved = true;
    }

    function isSolved() public view returns(bool){
        return solved;
    }
}