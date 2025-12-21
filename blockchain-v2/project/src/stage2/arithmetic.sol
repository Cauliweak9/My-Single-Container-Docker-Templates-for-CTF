// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Swap{
    uint public cat_coin_supply;
    uint public dog_coin_supply;
    uint public player_cat_coin_amount;
    uint public player_dog_coin_amount;
    bool get_airdrop;

    constructor(){
        cat_coin_supply = 10000;
        dog_coin_supply = 10000;
    }

    modifier airdrop_received{
        require(!get_airdrop, "Airdrop received.");
        _;
    }

    function airdrop() public airdrop_received{
        cat_coin_supply -= 1000;
        player_cat_coin_amount += 1000;
        get_airdrop = true;
    }

    function get_swap_price(uint from, uint to, uint amount) public pure returns(uint){
        return (amount * to / from);
    }

    function swap_cat_to_dog(uint amount) public{
        require(player_cat_coin_amount >= amount, "Not enough cat coins to swap.");
        uint swap_price = get_swap_price(cat_coin_supply, dog_coin_supply, amount);
        require(dog_coin_supply >= swap_price, "Not enough dog coins for swap.");

        player_cat_coin_amount -= amount;
        cat_coin_supply += amount;
        player_dog_coin_amount += swap_price;
        dog_coin_supply -= swap_price;
    }

    function swap_dog_to_cat(uint amount) public{
        require(player_dog_coin_amount >= amount, "Not enough dog coins to swap.");
        uint swap_price = get_swap_price(dog_coin_supply, cat_coin_supply, amount);
        require(cat_coin_supply >= swap_price, "Not enough cat coins for swap.");
        
        player_dog_coin_amount -= amount;
        dog_coin_supply += amount;
        player_cat_coin_amount += swap_price;
        cat_coin_supply -= swap_price;
    }

    function isSolved() public view returns(bool){
        return (cat_coin_supply == 0 || dog_coin_supply == 0);
    }
    
}