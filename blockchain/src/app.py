import requests
import json
from flask import Flask, request, jsonify, render_template
from utils.interaction import initialization, new_instance, get_flag


app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False  # 保持与 JSON-RPC 紧凑格式一致

challenge_address = ""
player_private_key = ""
banned_ips = set()


def forward_request(url_suffix=""):
    """通用请求转发函数"""
    target_url = f"http://localhost:8545{url_suffix}"
    headers = {key: value for key, value in request.headers if key.lower() != "host"}

    try:
        # 使用 streaming 方式处理大请求体
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            stream=True,
            timeout=30,  # 设置超时时间
        )

        # 构造代理响应
        return (
            response.content,
            response.status_code,
            [(name, value) for (name, value) in response.raw.headers.items()],
        )
    except requests.exceptions.RequestException as e:
        return (
            jsonify(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": f"Gateway error: {str(e)}"},
                    "id": None,
                }
            ),
            500,
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ide")
def ide():
    return render_template("ide.html")


@app.route("/rpc", methods=["POST", "OPTIONS"])
def rpc_proxy():
    client_ip = request.remote_addr

    # 拦截被封禁的 IP（仅针对 POST 请求）
    if request.method == "POST" and client_ip in banned_ips:
        return (
            jsonify(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -403, "message": "Get a life, cheater..."},
                    "id": None,
                }
            ),
            403,
        )

    # 处理 OPTIONS 请求
    if request.method == "OPTIONS":
        return forward_request(request.path)

    # 处理 POST 请求
    try:
        data = request.get_json()

        # 安全检查：检测到 anvil 方法立即封禁
        if "method" in data and "anvil" in data["method"].lower():
            banned_ips.add(client_ip)
            return jsonify(
                {
                    "jsonrpc": "2.0",
                    "id": data.get("id", 0),
                    "error": {
                        "code": -114514,
                        "message": "No shortcuts, dumbass! No more RPC for you!",
                    },
                }
            )

        # 转发正常请求
        return forward_request()

    except json.JSONDecodeError:
        return (
            jsonify(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None,
                }
            ),
            400,
        )


@app.route("/api/initialization", methods=["POST"])
def initialize():
    global challenge_address, player_private_key
    challenge_address, player_private_key = initialization()
    return jsonify(
        {"challenge_address": challenge_address, "private_key": player_private_key}
    )


@app.route("/api/create_instance", methods=["POST"])
def create_instance():
    global challenge_address, player_private_key
    challenge_address = new_instance()
    return jsonify(
        {"challenge_address": challenge_address, "private_key": player_private_key}
    )


@app.route("/api/get_flag", methods=["POST"])
def check():
    solved, response = get_flag(challenge_address)
    return jsonify({"solved": solved, "message": response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
