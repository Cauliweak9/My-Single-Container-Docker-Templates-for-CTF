// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.13;

import "forge-ctf/CTFDeployer.sol";

import "src/stage7/basic_defi.sol";

contract Deploy is CTFDeployer {
    function deploy(address system, address player) internal override returns (address challenge) {
        vm.startBroadcast(system);

        challenge = address(new Aurora_Token());

        vm.stopBroadcast();
    }
}
