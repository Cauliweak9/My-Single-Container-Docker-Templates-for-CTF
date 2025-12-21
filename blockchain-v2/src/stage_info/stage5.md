> 本题返回的地址为合约Car的地址

没活了，随便设计了一个加油站和一辆车，但是你这加油站怎么还能预定啤酒的啊？

想拿到flag？把我的车加满油再说吧？顺带把我后备箱的油箱也一起装满好了！要钱？没有，烂命一条，爱给就给不给拉倒！

卧槽你tm酒驾开到另一个加油站是几个意思？！不是哥们你从哪里变出来的油啊？！

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Gas_Station{
    uint public beers;
    uint constant ratio = 2;
    uint public car_fuel;
    uint public car_balance;

    function order_beers(uint bottles) public{
    	// 可任意预定啤酒瓶数
        beers = bottles;
    }

    function refuel(uint value) public{
    	// 1:2比例加油
        require(car_balance >= value, "Not enough balance.");
        car_balance -= value;
        car_fuel += value * ratio;
    }
}

contract Car{
    address public current_gas_station;
    uint public fuel = 10;
    uint public balance = 15;

    constructor(address gas_station){
        current_gas_station = gas_station;
    }

    function order_beers(uint amount) public{
        (bool success,) = current_gas_station.delegatecall(abi.encodeWithSignature("order_beers(uint256)",amount));
        require(success, "Failed to order beer.");
    }

    function refuel(uint value) public{
        (bool success,) = current_gas_station.delegatecall(abi.encodeWithSignature("refuel(uint256)",value));
        require(success, "Refuel failed.");
    }

    function isSolved() public view returns(bool){
        return (fuel >= 10000);
    }
}
```

