#  Blockchain Docker Template

##  Intro  简介

This template refers to [Hexens/remedy-ctf-2025](https://github.com/Hexens/remedy-ctf-2025), [paradigmxyz/paradigm-ctf-infrastructure: Public infra related to hosting Paradigm CTF](https://github.com/paradigmxyz/paradigm-ctf-infrastructure) and [ctf-docker-template/web-flask-python_3.10 at main · CTF-Archives/ctf-docker-template](https://github.com/CTF-Archives/ctf-docker-template/tree/main/web-flask-python_3.10). The `project` folder holds the challenge `Diamond Heist` from RemedyCTF 2025.

本模板参考了如上的三个repo。`project`文件夹中是RemedyCTF 2025的题目`Diamond Heist`。

~~Totally an ugly chimera bruh...   根本就是个丑陋的奇美拉，呃呃...~~



##  Dockerfile

The nodejs part is for an intended but unfinished feature: a native IDE in the instance. You may ignore it, and delete it if you want, but remember to delete the route and logic in app.py and the `ide.html` in `templates` folder.

Nodejs部分是留给一个预期的但是未实现的功能：一个内置在靶机中的IDE。你可以忽略它，甚至删掉它，但是记得删掉路由、逻辑和对应的文件。



Used supervisord to manage multiple processes, but during this process anvil was up without a random mnemonic like Remedy does, so the mnemonic is the good old `test junk` stuff, which means the wallet and the accounts are always be the same. In order to implement the dynamic private key and challenge address, I chose another dumb\*ss method which will be mentioned later.

使用了supervisord管理多进程，但是这个过程中anvil并没有像Remedy那边那样被指定随机的助记词就启动了，因此助记词是那一坨默认的`test junk`，这也就意味着钱包和账户是固定的。为了实现动态私钥和题目地址，我用了另一个非常铸币的办法，一会儿会提到。



**I do not guarantee the Dockerfile is the most accurate one (because I'm not sure if some of the libs are used, e.g. socat), but it runs, so I decided to ignore all that sh*t I wrote and let it be.**

**我不保证这个Dockerfile是最准确的（因为我不确定有些库是否被用到了，比如socat），但是它能跑，所以我就懒得管自己写的史了，随它去吧**。



> Please download the intended solc binary from [Releases · ethereum/solidity](https://github.com/ethereum/solidity/releases) in advance if you want to use the container in an environment without internet access, which is the `solc-static-linux` is for.
>
> 如果你希望在一个不出网的环境使用该容器，请提前从[Releases · ethereum/solidity](https://github.com/ethereum/solidity/releases)下载你需要的solc二进制文件，也就是这里`solc-static-linux`的意义所在。



##  app.py

A simple Flask app with several api routes acting as a bridge between frontend and the Anvil blockchain.

一个简单的Flask应用，内置若干个api路由充当前端和Anvil区块链的中介。



The api routes are called with fetch using the JavaScript written in `index.html`, meanwhile the rpc route will forward the request to the Anvil RPC if it is "valid".

API路由由`index.html`中的JS代码使用fetch进行请求调用，而RPC路由则会转发“合法”的请求到Anvil的RPC。



##  utils

Main logic interacting with the Anvil blockchain. `accounts.py` is excerpted from [remedy-ctf-2025/paradigm-ctf-infrastructure/paradigmctf.py/ctf_server/types/\__init__.py](https://github.com/Hexens/remedy-ctf-2025/blob/main/paradigm-ctf-infrastructure/paradigmctf.py/ctf_server/types/__init__.py), and `interaction.py` is mainly excerpted from [remedy-ctf-2025/paradigm-ctf-infrastructure/paradigmctf.py/ctf_launchers/utils.py](https://github.com/Hexens/remedy-ctf-2025/blob/main/paradigm-ctf-infrastructure/paradigmctf.py/ctf_launchers/utils.py)

和Anvil区块链交互的主逻辑，两个Python文件分别节选自对应的repo中。



The only two differences are the `--use /usr/bin/solc` in `deploy()` which means using the specific solc binary to compile and `anvil_setBalance` requests to "initialize" a random wallet generated from a random mnemonic. Pretty dumb*ss way to implement this if you ask me, but whatever, I'm too lazy lol.

唯二的区别是`deploy()`中加入的`--use`参数，这个表示使用指定的solc文件进行编译，另一个是`anvil_setBalance`请求以“初始化”一个随机助记词生成的随机钱包。我觉得这方法挺煞笔的，但无所谓了，懒了。



> Due to the powerful API methods of anvil, any user who requests the RPC with `anvil` in his/her JSON-RPC API method will be banned from the RPC, and the only way is to destroy and create a new instance. (Yes I use CTFd)
>
> 由于anvil的超强API方法，任何用户在往RPC发送请求时使用的方法带`anvil`都会直接被ban掉，无法再次使用该RPC，因此该用户只能销毁并重新创建一个新实例。（是的，我用的是CTFd）