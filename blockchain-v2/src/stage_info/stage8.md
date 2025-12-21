> 本题返回的地址为合约Proxy的地址

使用可升级代理合约存钱真是一件美事...卧槽我忘记设置提款函数了！还好我有个备用方案，大伙投票支持我更新合约就行...

什么叫看到我钱丢了你们乐坏了？！笑就完了，还不投票帮我？！我[CENSORED]...

> 小提示：如果只是用一个EOA地址做不出来，要不试试用两个？什么？你问我哪里来的第2个地址？你猜φ(゜▽゜*)♪

代理合约`proxy.sol`：

```solidity
// proxy.sol
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
```

治理合约`governance.sol`：

```solidity
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
```

金库函数`vault.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Vault{
    event Deposit(address indexed user, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);

    function deposit() public payable {
        require(msg.value > 0, "Must send some Ether");
        emit Deposit(msg.sender, msg.value);
    }

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
```

