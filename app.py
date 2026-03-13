import qrcode
import uuid
from io import BytesIO
from flask import Flask, send_file, jsonify, make_response

app = Flask(__name__)

# 模拟：存储登录凭证（实际应存在Redis/数据库，带过期时间）
login_ticket_map = {}


@app.route('/get_login_qrcode', methods=['GET'])
def get_login_qrcode():
    """生成登录二维码，返回图片数据流（或Base64）"""
    # 1. 生成唯一登录凭证（ticket），用于关联扫码和登录状态
    login_ticket = str(uuid.uuid4())
    # 2. 构造扫码登录的链接（前端扫码后，手机端访问该链接完成授权）
    #    实际场景：链接指向你的手机端授权页面，携带ticket
    qr_content = f"https://your-domain.com/mobile/login?ticket={login_ticket}"
    # 3. 存储ticket（模拟，实际用Redis，设置5分钟过期）
    login_ticket_map[login_ticket] = {"status": "waiting", "user_id": None}

    # ========== 方式1：生成二维码图片，返回文件数据流 ==========
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 将图片写入BytesIO（内存流，无需保存到本地文件）
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)  # 重置文件指针

    # 返回图片文件（前端直接访问该接口即可显示二维码）
    return send_file(
        img_io,
        mimetype='image/png',
        as_attachment=False,  # 不下载，直接展示
        download_name='login_qrcode.png'
    )

    # ========== 方式2：返回Base64编码（前端更灵活） ==========
    # import base64
    # img_io = BytesIO()
    # img.save(img_io, 'PNG')
    # img_io.seek(0)
    # img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    # return jsonify({
    #     "code": 200,
    #     "data": {
    #         "ticket": login_ticket,
    #         "qrcode_base64": f"data:image/png;base64,{img_base64}"
    #     }
    # })


@app.route('/check_login_status/<ticket>', methods=['GET'])
def check_login_status(ticket):
    """前端轮询该接口，检查扫码登录状态"""
    if ticket not in login_ticket_map:
        return jsonify({"code": 404, "msg": "二维码已过期"})

    status = login_ticket_map[ticket]["status"]
    user_id = login_ticket_map[ticket]["user_id"]

    if status == "success":
        # 生成登录token（实际用JWT等）
        login_token = f"token_{user_id}_{ticket}"
        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {"token": login_token, "user_id": user_id}
        })
    else:
        return jsonify({"code": 202, "msg": "等待扫码/授权"})


@app.route('/mobile_login/<ticket>/<user_id>', methods=['GET'])
def mobile_login(ticket, user_id):
    """手机端扫码后调用该接口，完成授权（模拟）"""
    if ticket not in login_ticket_map:
        return jsonify({"code": 404, "msg": "二维码已过期"})

    # 更新登录状态为成功
    login_ticket_map[ticket]["status"] = "success"
    login_ticket_map[ticket]["user_id"] = user_id
    return jsonify({"code": 200, "msg": "授权成功，电脑端即将登录"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
