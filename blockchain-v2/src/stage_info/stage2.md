> 本题返回的地址为合约Swap的地址

从本题开始，我们将陆续给你一些有漏洞的合约，你需要根据你刚刚学到的知识（以及你从别的地方学到的知识）来攻击这些合约以达到某些条件，不过由于代码量问题我会尽量给一些注释，但是注释之中是否存在漏洞就需要各位自行判断了

本页下方是实例控制台，其中左下角的按钮是创建新实例，会返回本题实例的合约地址以及你的账户私钥（以防你忘了），而右下角的按钮是提交实例，也就是如果你满足了预定的条件（一般是让函数`isSolved`返回True），你点击这个按钮就能得到flag了

>  如果你本题的实例出问题了可以再次点击左下角的按钮刷新实例，不过需要注意：此时本题对应的题目合约地址会发生改变，实在不行就重启靶机吧www

还是有点晕乎乎的？那让我们以本题为例：我们设计了一个代币的交换所，同时为你准备了一个一次性的空投函数`airdrop()`，而**你的目标就是要使得`isSolved()`函数返回值为True**，在本题中则是将两种代币之一从交换所中全部偷走

```solidity
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
    	// 只能获取一次空投
        require(!get_airdrop, "Airdrop received.");
        _;
    }

    function airdrop() public airdrop_received{
        cat_coin_supply -= 1000;
        player_cat_coin_amount += 1000;
        get_airdrop = true;
    }

    function get_swap_price(uint from, uint to, uint amount) public pure returns(uint){
    	// 汇率计算，根据持有的两种代币的比例计算from代币的价值
        return (amount * to / from);
    }

    function swap_cat_to_dog(uint amount) public{
    	// 根据动态汇率将指定量的Cat Coin换为Dog Coin
        require(player_cat_coin_amount >= amount, "Not enough cat coins to swap.");
        uint swap_price = get_swap_price(cat_coin_supply, dog_coin_supply, amount);
        require(dog_coin_supply >= swap_price, "Not enough dog coins for swap.");

        player_cat_coin_amount -= amount;
        cat_coin_supply += amount;
        player_dog_coin_amount += swap_price;
        dog_coin_supply -= swap_price;
    }

    function swap_dog_to_cat(uint amount) public{
    	// 根据动态汇率将指定量的Dog Coin换为Cat Coin
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
```

