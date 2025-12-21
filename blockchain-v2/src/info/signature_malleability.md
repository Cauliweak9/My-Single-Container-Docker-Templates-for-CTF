#  签名复用&签名伪造

> 本文的LaTeX渲染有很大的问题，各位将就着看吧

区块链作为一套去中心化的系统，它需要一个手段，既能够摆脱中心化实体，又能使得参与者验证交易、确认所有权并维护数据完整性，而这个手段就是我们本篇将要提及的数字签名（Digital Signatures）

##  0. 以太坊的数字签名原理

> 坐稳了，这一部分是我们的密码学部分，会有一些数学知识

以太坊使用的数字签名算法是椭圆曲线数字签名算法（Elliptic Curve Digital Signature Algorithm, ECDSA），也就是说这种数字签名是依赖于椭圆曲线实现的，具体的椭圆曲线叫SECP256k1曲线，它的方程长这样：
$$
y^2=x^3+7
$$
那么根据初中知识，我们能很快知道这个曲线是关于X轴对称的，而这对我们进行签名伪造至关重要

在ECDSA中，一个签名由一组值$(r,s)$表示，其中`r`是签名过程中计算出的公钥的X坐标，而这个点是由$(x,y)=k*G$这样计算得到的，其中`k`满足$1 < k < n$（`n`表示的是SECP256k1中规定的点的个数，即`0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141`），而这里签名使用的k一般是通过私钥计算得到的；而`G`则是我们所说的生成点，这个点使用SEC格式（高效加密标准，The Standards for Efficient Cryptography）进行表示的结果是`0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798`；`s`则是通过公式$s = k^{-1} * (e + d*r)\bmod{n}$计算得到的，其中`e`表示`hash(msg)`，而`d`表示签名者私钥

根据刚才提到的曲线对称性，一个X坐标可以对应2个Y坐标，也就是说实际上可能存在2个合法的点，因此我们需要一个额外的恢复值`v`来决定签名者的公钥，而在以太坊黄皮书中已经规定了一个合法的签名需要满足的条件：
$$
0<s<\frac{n}{2}+1,v\in \{27,28\}
$$
当然，话是这么说...

##  1. 签名伪造

虽然黄皮书已经规范了合法的签名值，但是在[EIP-2](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-2.md)中仍然允许满足$0<s<n$的`s`参与交易，也就是说EIP-2认为两个点均为合法的，而这就是我们签名伪造（Signature Malleability）的基础

根据上面的理论，我们可以推出如下的结论：**如果$(r,s)$是一组合法的签名，那么根据SECP256k1的X轴对称性，$(r, -s\bmod{n})$也必然是一组合法的签名**

因此我们可以有如下的Python代码生成另一个“合法”的签名：

```python
from web3 import Web3
from eth_account.messages import encode_defunct

w3 = Web3()
# Turn the message hash into bytes
message_hash = bytes.fromhex("deadbeef")

# Your private key
private_key = "My Private Key"  # Replace with your private key (DO NOT SHARE THIS)

# Sign the message
signed_message = w3.eth.account.signHash(message_hash, private_key=private_key)

# View the original signature
print("Signature:", signed_message.signature.hex())
print("v:", signed_message.v)
print("r:", hex(signed_message.r))
print("s:", hex(signed_message.s))
print(
    f'Original Signature: [{signed_message.v},"{hex(signed_message.r)}","{hex(signed_message.s)}"]'
)

# Another valid signature: (r,-s mod n)
manipulated_v = (
    signed_message.v + 1 if signed_message.v % 2 != 0 else signed_message.v - 1
)
manipulated_r = signed_message.r
manipulated_s = (
    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    - signed_message.s
)
print(
    f'Manipulated Signature: [{manipulated_v},"{hex(manipulated_r)}","{hex(manipulated_s)}"]'
)
```

对于两组`v,r,s`，Solidity中的`ecrecover(bytes32 hash, uint8 v, bytes32 r, bytes32 s)`函数都会返回同一个地址，这个地址就是你的私钥所对应的地址

##  2. 签名复用

顾名思义，签名复用（Signature Replay）就是指开发者在设计合约逻辑的时候没有考虑到签名重复利用的可能性，最终导致同一个签名被使用多次，进而引发一系列问题

比如我们有一个投票系统，每个人需要对某个特定的信息进行签名才能完成投票，理论上这个签名应该是一次性的，但是这个系统并没有做检查和处理，最后就导致有人使用同一个签名进行了多次的投票

解决方案也相对比较简单：记录已被使用的签名信息，以及在需要签名的信息中添加一些具有时间性质的参数，比如一个递增的nonce

> 当然，如果你的项目是跨链的话，最好添加chainId参数防止跨链的签名复用