// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Gas_Station{
    uint public beers;
    uint constant ratio = 2;
    uint public car_fuel;
    uint public car_balance;

    function order_beers(uint bottles) public{
        beers = bottles;
    }

    function refuel(uint value) public{
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