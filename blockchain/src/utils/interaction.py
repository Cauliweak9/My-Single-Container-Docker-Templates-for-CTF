import os
import subprocess
from typing import Dict
from web3 import Web3
from web3.types import RPCResponse
from eth_abi import abi
from eth_account.hdaccount import generate_mnemonic
import random
from utils.account import get_account, get_player_account

ANVIL_INSTANCE = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
DEFAULT_MNEMONIC = "test test test test test test test test test test test junk"
ETH = 10**18
FLAG = os.getenv("FLAG", "Aurora{A_t0tal_br3akth7ough!!!}")
mnemonic = ""


def check_error(resp: RPCResponse):
    if "error" in resp:
        raise Exception("rpc exception", resp["error"])


def anvil_autoImpersonateAccount(web3: Web3, enabled: bool):
    check_error(web3.provider.make_request("anvil_autoImpersonateAccount", [enabled]))


def anvil_setBalance(web3: Web3, address: str, amount: str):
    check_error(web3.provider.make_request("anvil_setBalance", [address, amount]))


def deploy(
    web3: Web3,
    project_location: str,
    mnemonic: str,
    deploy_script: str = "script/Deploy.s.sol:Deploy",
    env: Dict = {},
) -> str:
    anvil_autoImpersonateAccount(web3, True)

    rfd, wfd = os.pipe2(os.O_NONBLOCK)

    proc = subprocess.Popen(
        args=[
            "/opt/foundry/bin/forge",
            "script",
            "--rpc-url",
            web3.provider.endpoint_uri,
            "--out",
            "/artifacts/out",
            "--cache-path",
            "/artifacts/cache",
            "--use",
            "/usr/bin/solc",
            "--broadcast",
            "--unlocked",
            "--sender",
            "0x0000000000000000000000000000000000000000",
            deploy_script,
        ],
        env={
            "PATH": "/opt/huff/bin:/opt/foundry/bin:/usr/bin:"
            + os.getenv("PATH", "/fake"),
            "MNEMONIC": mnemonic,
            "OUTPUT_FILE": f"/proc/self/fd/{wfd}",
        }
        | env,
        pass_fds=[wfd],
        cwd=project_location,
        text=True,
        encoding="utf8",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()

    anvil_autoImpersonateAccount(web3, False)

    if proc.returncode != 0:
        print(stdout)
        print(stderr)
        raise Exception(f"forge failed to run: {stderr}")

    result = os.read(rfd, 256).decode("utf8")

    os.close(rfd)
    os.close(wfd)

    return result


def manual_set_wallet(mnemonic: str):
    for i in range(10):
        account = get_account(mnemonic, i)
        default_account = get_account(DEFAULT_MNEMONIC, i)
        anvil_setBalance(ANVIL_INSTANCE, account.address, str(10000 * ETH))
        anvil_setBalance(ANVIL_INSTANCE, default_account.address, "0")


def initialization():
    global mnemonic
    mnemonic = generate_mnemonic(12, lang="english")
    manual_set_wallet(mnemonic)
    challenge_address = deploy(
        ANVIL_INSTANCE, "/app/project", mnemonic=mnemonic, env={}
    )
    player_private_key = get_player_account(mnemonic).key.hex()
    return (challenge_address, player_private_key)


def new_instance():
    global mnemonic
    challenge_address = deploy(ANVIL_INSTANCE, "/app/project", mnemonic, env={})
    return challenge_address


def is_solved(address: str):
    (result,) = abi.decode(
        ["bool"],
        ANVIL_INSTANCE.eth.call(
            {"to": address, "data": ANVIL_INSTANCE.keccak(text="isSolved()")[:4]}
        ),
    )
    return result


def get_flag(address: str):
    solved = is_solved(address)
    if solved:
        return (
            solved,
            random.choice(
                [
                    f"恭喜！(/≧▽≦)/这是你的flag：{FLAG}",
                    f"哇，我都看入迷了！(☆▽☆)那就送你flag吧：{FLAG}",
                    f"大~神~降~临~！为大神献上flag！{FLAG}",
                ]
            ),
        )
    else:
        return (
            solved,
            random.choice(
                [
                    "好像没通过欸o(TヘTo)...要不再试试？",
                    "好像有地方出问题了...但一定不是我的错！（︶^︶）",
                    "我这边没看到你满足条件欸(´ｰ∀ｰ`)...要不你再调一下看看？",
                ]
            ),
        )
