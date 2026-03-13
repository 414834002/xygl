from flask import Flask, jsonify, request
import qrcode
import uuid
import base64

app = Flask(__name__)

# 存储登录状态，这里简单用字典模拟，实际可使用数据库
login_states = {}

@app.route('/api/generate_qr', methods=['GET'])
def generate_qr():
    token = str(uuid.uuid4())  # 生成唯一令牌
    qr_content = f"https://your-render-url/api/confirm_login?token={token}"  # 替换成实际Render域名
    img = qrcode.make(qr_content)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    qr_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
    login_states[token] = 'pending'
    return jsonify({"code": 200, "data": {"token": token, "qr_image": f"data:image/png;base64,{qr_base64}"}})

@app.route('/api/check_login', methods=['GET'])
def check_login():
    token = request.args.get('token')
    if token not in login_states:
        return jsonify({"code": 400, "msg": "无效的令牌"})
    return jsonify({"code": 200, "data": {"status": login_states[token]}})

@app.route('/api/confirm_login', methods=['GET'])
def confirm_login():
    token = request.args.get('token')
    if token not in login_states:
        return "<h1>无效的令牌</h1>"
    login_states[token] = 'confirmed'
    return "<h1>登录成功！请返回电脑端查看</h1>"

if __name__ == '__main__':
    app.run(debug=True)