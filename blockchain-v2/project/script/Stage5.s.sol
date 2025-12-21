// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.13;

import "forge-ctf/CTFDeployer.sol";

import "src/stage5/delegatecall.sol";

contract Deploy is CTFDeployer {
    function deploy(address system, address player) internal override returns (address challenge) {
        vm.startBroadcast(system);

        address gas_station = address(new Gas_Station());
        challenge = address(new Car(gas_station));

        vm.stopBroadcast();
    }
}
