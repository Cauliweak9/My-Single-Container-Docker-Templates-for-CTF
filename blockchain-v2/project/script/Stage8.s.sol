// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.13;

import "forge-ctf/CTFDeployer.sol";

import "src/stage8/governance.sol";
import { Proxy } from "src/stage8/proxy.sol";
import "src/stage8/vault.sol";

contract Deploy is CTFDeployer {
    function deploy(address system, address player) internal override returns (address challenge) {
        vm.startBroadcast(system);

        address governance = address(new Governance(player));
        address vault = address(new Vault());
        challenge = address(new Proxy(governance, vault));
        Vault(challenge).deposit{value: 100 ether}();

        vm.stopBroadcast();
    }
}
