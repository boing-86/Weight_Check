from flask import Flask, request, render_template, redirect, session
from datetime import datetime
import requests
import bcrypt
import json
import re


BACKEND_ADDRESS = "http://127.0.0.1:5000"

app = Flask(__name__)
app.secret_key = "123456129efl32089df@#$fd"


@app.route('/', methods=['GET'])
def index():
    if 'user_id' in session:
        return redirect('/main')
    return redirect('login')

@app.route('/main', methods=['GET'])
def page_main():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def page_login():
    if 'user_id' in session:
        return redirect('/main')
    return render_template('login.html')

###################### APIs ########################

@app.route('/api/login', methods=['POST'])
def get_weight():
    user_id = request.form['username']
    user_pw = request.form['password']
    id_re = re.compile('/^(?=.*[a-zA-Z])[-a-zA-Z0-9_.]{2,10}$/;')
    pw_re = re.compile('/^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;')
    
    if id_re.match(user_id) == None or pw_re.match(user_pw) == None:
        return json.dumps({'error': "아이디 또는 비밀번호 형식이 다릅니다."})

    password = requests.post(BACKEND_ADDRESS + "/get/password", json={'user_id': user_id}).text
    bcrypt_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    if user_pw == bcrypt_pw:
        session['user_id'] = user_id
        return redirect('/main')
    
    return json.dumps({'error': "비밀번호가 다릅니다."})

@app.route('/api/logout', methods=['POST'])
def log_out():
    session.pop('user_id')
    return redirect('/login')


@app.route('/api/main/exp_weight')
def get_exp_weight():
    return requests.post(BACKEND_ADDRESS + "/weight").json()

@app.route('/api/main/result')
def get_result():
    data = request.get_json()
    data['user_key'] = session['user_id']
    data['finish_time'] = datetime.now().strftime('%Y %m %d %H %M %S')

    requests.post(BACKEND_ADDRESS + "/save/weight", json=data)
    
    return 'saved'

################# T  E  S  T ##################

@app.route('/api/bi')
def get_bcrypt_str():
    password = request.args.get('pw')
    bcrypt_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    return bcrypt_pw

@app.route('/api')
def test():
    path = request.path
    host = request.host_url
    
    return {"path":path, "host": host}



if __name__ == "__main__":  # 웹사이트를 호스팅하여 접속자에게 보여주기 위한 부분
   app.run(host="0.0.0.0", port = "5000")
   # host는 현재 라즈베리파이의 내부 IP, port는 임의로 설정
   # 해당 내부 IP와 port를 포트포워딩 해두면 외부에서도 접속가능