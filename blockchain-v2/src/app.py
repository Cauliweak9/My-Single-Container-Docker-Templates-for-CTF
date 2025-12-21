from flask import Flask, render_template, redirect, url_for, request, jsonify, abort
import re
import json
import requests
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
import os
from utils.interaction import AnvilManager


app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False  # 保持与 JSON-RPC 紧凑格式一致

challenge_addresses = [""] * 7
player_private_key = ""
anvil_instance = None
# 全局变量记录完成状态
completed = set()
banned_ips = set()

door_name = [
    "浅梦轻眠",
    "溢梦虚空",
    "梦隙拒流",
    "盗梦空间",
    "庄周梦蝶",
    "千面一人",
    "商海如幻",
    "镜花水月",
]
markdown_contents = [
    "basics",
    "arithmetic",
    "denial_of_service",
    "reentrancy",
    "delegatecall",
    "signature_malleability",
    "basic_defi",
    "final",
]


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


# 检查第8扇门访问权限的装饰器
def check_door8_access(f):
    def wrapper(door_number):
        if door_number == 8 and len(completed) < 7:
            return render_template("locked.html", completed_count=len(completed))
        return f(door_number)

    wrapper.__name__ = f.__name__
    return wrapper


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
    return render_template(
        "index.html",
        door_name=door_name,
        all_visited=len(completed) >= 7,
        completed=completed,
        completed_count=len(completed),
        markdown_contents=markdown_contents,
    )


@app.route("/<string:content>")
def door(content):
    if content in markdown_contents:
        door_number = markdown_contents.index(content) + 1

        # 读取Markdown内容
        try:
            with open(f"/app/src/info/{content}.md", "r", encoding="utf-8") as f:
                md_content = render_markdown(f.read())
        except FileNotFoundError:
            md_content = render_markdown(f"# 第{door_number}扇门\n\n内容未找到")

        return render_template(
            "door.html",
            door_number=door_number,
            door_name=door_name,
            content=md_content,
            content_name=content,
            is_special=door_number == 8,
            completed=completed,
            completed_count=len(completed),
        )
    abort(404)


@app.route("/stage/<string:content>")
def stage(content):
    if content in markdown_contents:
        door_number = markdown_contents.index(content) + 1

        # 检查第8扇门访问权限
        if door_number == 8 and len(completed) < 7:
            return render_template(
                "locked.html", completed_count=len(completed), completed=completed
            )

        # 读取阶段说明
        stage_info = ""
        try:
            with open(
                f"/app/src/stage_info/stage{door_number}.md", "r", encoding="utf-8"
            ) as f:
                stage_info = render_markdown(f.read())
        except FileNotFoundError:
            stage_info = "阶段说明未找到"

        # 检查是否有现有的挑战地址
        existing_challenge = ""
        if 2 <= door_number <= 8:
            idx = door_number - 2  # challenge_addresses从第2扇门开始
            if idx < len(challenge_addresses) and challenge_addresses[idx]:
                existing_challenge = challenge_addresses[idx]

        return render_template(
            "stage.html",
            door_name=door_name,
            door_number=door_number,
            content_name=content,
            stage_info=stage_info,
            existing_challenge=existing_challenge,
            private_key=player_private_key,
            completed=completed,
            completed_count=len(completed),
        )
    abort(404)


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
    global challenge_addresses, player_private_key
    data = request.json
    door_number = data.get("door_number")

    if not door_number or door_number < 2 or door_number > 8:
        return jsonify({"error": "Invalid door number"}), 400

    challenge_addresses[door_number - 2] = anvil_instance.new_instance(door_number)
    return jsonify(
        {
            "challenge_address": challenge_addresses[door_number - 2],
            "private_key": player_private_key,
        }
    )


@app.route("/api/submit_instance", methods=["POST"])
def submit_instance():
    data = request.json
    door_number = data.get("door_number", 0)
    address = data.get("address", "")

    if door_number > 1:
        address = challenge_addresses[door_number - 2]
    solved, response = anvil_instance.get_flag(door_number, address)

    if solved and door_number not in completed:
        completed.add(door_number)

    return jsonify(
        {
            "solved": solved,
            "message": response,
        }
    )


@app.route("/progress")
def progress():
    return jsonify({"completed_count": len(completed), "completed": list(completed)})


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
