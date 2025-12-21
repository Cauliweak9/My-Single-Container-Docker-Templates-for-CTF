// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.13;

import "forge-ctf/CTFDeployer.sol";

import "src/stage6/signature.sol";

contract Deploy is CTFDeployer {
    function deploy(address system, address player) internal override returns (address challenge) {
        vm.startBroadcast(system);

        challenge = address(new Voting(player));

        vm.stopBroadcast();
    }
}
