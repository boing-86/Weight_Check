from flask import Flask, request, render_template, redirect, session
import requests
import bcrypt


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
    # if 'user_id' in session:
    #     return redirect('/main')
    return render_template('login.html')

###################### APIs ########################

@app.route('/api/login', methods=['POST'])
def get_weight():
    user_id = request.form['username']
    user_pw = request.form['password']

    password = requests.post(BACKEND_ADDRESS + "/get/password", json={'user_id': user_id}).text
    bcrypt_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    if user_pw == bcrypt_pw:
        session['user_id'] = user_id
        return redirect('/main')
    
    return redirect('/login')

@app.route('/api/logout', methods=['POST'])
def log_out():
    session.pop('user_id')
    return redirect('/login')

@app.route('/api/main/real_weight')
def get_real_weight():
    return 'Hello'

@app.route('/api/main/exp_weight')
def get_exp_weight():
    return 'Hello'

@app.route('/api/main/result')
def get_result():
    return 'Hello'

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