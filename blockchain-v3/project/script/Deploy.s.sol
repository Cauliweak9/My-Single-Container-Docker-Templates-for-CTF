// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.30;

import "forge-ctf/CTFDeployer.sol";

import "src/challenge.sol";

contract Deploy is CTFDeployer {
    function deploy(address system, address player) internal override returns (address challenge) {
        vm.startBroadcast(system);

        challenge = address(new Example());

        vm.stopBroadcast();
    }
}