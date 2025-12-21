// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.13;

import "forge-ctf/CTFDeployer.sol";

import "src/stage3/denial_of_service.sol";

contract Deploy is CTFDeployer {
    function deploy(
        address system,
        address player
    ) internal override returns (address challenge) {
        vm.startBroadcast(system);

        challenge = address(new Sponsoring{value: 2 ether}());

        vm.stopBroadcast();
    }
}
