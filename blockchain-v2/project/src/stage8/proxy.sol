// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Governance{
    function getCurrentVotes(address owner) external view returns(uint);
    function getThreshold() external view returns(uint);
}

contract Proxy{
    event Upgrade(address indexed previousImplementation, address newImplementation);

    address public governance;
    address public implementation;

    constructor(address _governance, address _implementation){
        governance = _governance;
        implementation = _implementation;
    }

    modifier onlyProxy{
        require(msg.sender == address(this), "Not called by proxy contract.");
        _;
    }

    function governanceCall(bytes calldata data) public{
        require(Governance(governance).getCurrentVotes(msg.sender) >= Governance(governance).getThreshold(), "Not enough votes.");
        (bool success,) = address(this).call(data);
        require(success);
    }

    function upgradeTo(address _implementation) public onlyProxy{
        require(_implementation.code.length > 0, "Address is not a contract.");
        address temp = implementation;
        implementation = _implementation;
        emit Upgrade(temp,_implementation);
    }

    function _delegate() internal virtual {
        address _implementation = implementation;
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(
                gas(),
                _implementation,
                0,
                calldatasize(),
                0,
                0
            )
            returndatacopy(0, 0, returndatasize())

            switch result
            case 0 {
                revert(0, returndatasize())
            }
            default {
                return(0, returndatasize())
            }
        }
    }

    function isSolved() public view returns(bool){
        return address(this).balance == 0;
    }

    fallback() external payable {
        _delegate();
    }

    receive() external payable {
        _delegate();
    }
}