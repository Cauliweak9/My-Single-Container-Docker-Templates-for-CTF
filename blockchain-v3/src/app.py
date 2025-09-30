from flask import Flask, render_template, request, jsonify
import json
import requests
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from utils.interaction import AnvilManager


app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False  # 保持与 JSON-RPC 紧凑格式一致

challenge_address = ""
player_private_key = ""
anvil_instance = None
# 全局变量记录完成状态
completed = False
banned_ips = set()

markdown_contents = "description"

def render_markdown(content):
    extensions = [
        CodeHiliteExtension(noclasses=True, pygments_style="monokai"),
        FencedCodeExtension(),
        "pymdownx.arithmatex",  # 添加LaTeX支持
        "tables",
        "fenced_code",
    ]

    # 配置arithmatex扩展
    extension_configs = {
        "pymdownx.arithmatex": {
            "generic": True,  # 同时支持$...$和$$...$$
            "preview": False,  # 不显示实时预览
        }
    }

    return markdown.markdown(
        content, extensions=extensions, extension_configs=extension_configs
    )


# 404错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404



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
            timeout=120,  # 设置超时时间
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
    global challenge_address, player_private_key
    
    try:
        with open(f"/app/src/info/{markdown_contents}.md", "r", encoding="utf-8") as f:
            md_content = render_markdown(f.read())
    except FileNotFoundError:
        md_content = render_markdown(f"# 未找到题目描述文件")
    if challenge_address != "" and player_private_key != "":
        return render_template(
            "index.html",
            markdown_contents=md_content,
            challenge_address=challenge_address,
            player_private_key=player_private_key
        )
    return render_template(
        "index.html",
        markdown_contents=md_content,
    )



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


@app.route("/api/create_instance", methods=["POST"])
def create_instance():
    global challenge_address, player_private_key

    challenge_address = anvil_instance.new_instance()
    return jsonify(
        {
            "challenge_address": challenge_address,
            "private_key": player_private_key,
        }
    )


@app.route("/api/submit_instance", methods=["POST"])
def submit_instance():

    solved, response = anvil_instance.get_flag(challenge_address)

    return jsonify(
        {
            "solved": solved,
            "message": response,
        }
    )


@app.route("/debug")
def debug():
    with open("/tmp/anvil.log", "r") as file:
        data = file.read()
        file.close()
    return data


if __name__ == "__main__":
    anvil_instance = AnvilManager()
    player_private_key = anvil_instance.initialization()
    app.run(host="0.0.0.0", debug=False)
