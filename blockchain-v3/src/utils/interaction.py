import os
import subprocess
from typing import Dict, Optional
from web3 import Web3
from web3.types import RPCResponse
from eth_abi import abi
from eth_account.hdaccount import generate_mnemonic
import random
from utils.account import get_account, get_player_account

ANVIL_INSTANCE = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
DEFAULT_MNEMONIC = "test test test test test test test test test test test junk"
ETH = 10**18
FLAG = "Aurora{T3mpl@te_Mad3_By_Cauliweak9_o(=•ω＜=)ρ⌒☆}"

def check_error(resp: RPCResponse):
    if "error" in resp:
        raise Exception("rpc exception", resp["error"])


def anvil_autoImpersonateAccount(web3: Web3, enabled: bool):
    check_error(web3.provider.make_request("anvil_autoImpersonateAccount", [enabled]))

class AnvilManager:
    def __init__(self):
        self._mnemonic = None
        self.FLAG = FLAG
        with open("/tmp/anvil.log", "w") as file:
            ...

    def start_anvil(
        self,
        port: int = 8545,
        balance: int = 100000,
        block_time: Optional[int] = 1,
        hardfork: str = "prague",
        mnemonic: Optional[str] = None,
    ):
        """
        启动anvil本地节点

        Args:
            port: 要监听的端口号
            balance: 所有生成的钱包账户的初始余额
            block_time: 区块生成间隔时间(秒)，None表示不自动挖矿
            hardfork: 本地链硬分叉版本
            mnemonic: 生成钱包时使用的助记词
        """
        env = os.environ.copy()  # 复制当前环境变量
        env["RUST_LOG"] = "node,backend,api,rpc=warn"  # 添加/修改RUST_LOG变量
        cmd = [
            "anvil",
            "--port",
            str(port),
            "--hardfork",
            hardfork,
            "--balance",
            str(balance)
        ]
        if block_time is not None:
            cmd.extend(["--block-time", str(block_time)])
        if mnemonic is not None:
            cmd.extend(["--mnemonic", mnemonic])

        print(f"Starting anvil on port {port}...")
        _anvil_process = subprocess.Popen(
            args=cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            encoding="utf8",
            bufsize=1,
            universal_newlines=True,
        )

        # 实时输出日志的线程
        def log_output():
            while True:
                output = _anvil_process.stdout.readline()
                if output == "" and _anvil_process.poll() is not None:
                    break
                if output:
                    with open("/tmp/anvil.log", "w") as file:
                        file.write(f"[ANVIL] {output.strip()}\n")

        import threading

        log_thread = threading.Thread(target=log_output, daemon=True)
        log_thread.start()

    def deploy(
        self,
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
        
        anvil_autoImpersonateAccount(web3,False)

        if proc.returncode != 0:
            print(stdout)
            print(stderr)
            raise Exception(f"forge failed to run: {stderr}")

        result = os.read(rfd, 256).decode("utf8")

        os.close(rfd)
        os.close(wfd)

        return result

    def initialization(self):
        self._mnemonic = generate_mnemonic(12, lang="english")
        self.start_anvil(mnemonic=self._mnemonic)
        player_private_key = get_player_account(self._mnemonic).key.hex()
        return player_private_key

    def new_instance(self):
        web3_instance = ANVIL_INSTANCE
        mnemonic = self._mnemonic
        challenge_address = self.deploy(
            web3_instance,
            "/app/project",
            mnemonic,
            deploy_script=f"script/Deploy.s.sol:Deploy",
        )
        return challenge_address

    def is_solved(self, instance_address: str):
        web3_instance = ANVIL_INSTANCE
        (result,) = abi.decode(
            ["bool"],
            web3_instance.eth.call(
                {
                    "to": instance_address,
                    "data": web3_instance.keccak(text="isSolved()")[:4],
                }
            ),
        )
        return result
    

    def get_flag(self, address: str):
        solved = self.is_solved(address)
        if solved:
            return (
                solved,
                random.choice(
                    [
                        f"恭喜！(/≧▽≦)/这是你的flag：{self.FLAG}",
                        f"哇，我都看入迷了！(☆▽☆)那就送你flag吧：{self.FLAG}",
                        f"大~神~降~临~！为大神献上flag！{self.FLAG}",
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
