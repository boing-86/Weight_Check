from flask import Flask, request, render_template, redirect, session
from os import getenv
from datetime import datetime
import requests
import random
import bcrypt
import re

if not getenv('KurlyCheckBeHost') and not getenv('KurlyCheckBePort'):
    print("\033[31mFrontend(app.py) : make environment variable for BE server connection!\033[0m")

BACKEND_ADDRESS = f"http://{getenv('KurlyCheckBeHost')}:{getenv('KurlyCheckBePort')}"


def encrypt(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


app = Flask(__name__)
app.secret_key = encrypt(str(random.random()))


@app.route('/', methods=['GET'])
def index():
    if 'is_admin' in session:
        return redirect('/admin')
    if 'user_id' in session:
        return redirect('/main')
    return redirect('login')


@app.route('/main', methods=['GET'])
def page_main():
    return render_template('index.html')


@app.route('/admin', methods=['GET'])
def page_admin():
    return render_template('admin.html')


@app.route('/login', methods=['GET', 'POST'])
def page_login():
    form = {'id': '', 'pw': ''}
    if request.method == 'GET':
        is_login = 'user_id' in session
        is_admin = 'is_admin' in session
    else:
        form['id'] = request.form['username']
        form['pw'] = request.form['password']
        is_login, is_admin = try_login(form)
    
    if is_admin:
        return redirect('/admin')
    if is_login:
        return redirect('/main')
    return render_template('login.html', form=form)


# 아이디: 영문, 숫자조합 5~19글자
# 비밀번: 영문, 숫자, 특수문자 조합 8~16글자
def try_login(form):
    id_re = re.compile('[A-Za-z]+[A-Za-z0-9]{5,19}')
    pw_re = re.compile('(?=.*[a-zA-z])(?=.*[0-9])(?=.*[$`~!@$!%*#^?&\\(\\)\-_=+]).{8,16}')
    
    if id_re.match(form['id']) is None or pw_re.match(form['pw']) is None:
        return False, False
    
    data = requests.post(BACKEND_ADDRESS + "/get/password", json={'user_id': form['id']}).json()
    password = data['password']
    is_admin = data['is_admin']
    
    bcrypt_pw = encrypt(password)
    
    if form['pw'] == bcrypt_pw:
        session['user_id'] = form['id']
        return True, bool(is_admin)
    return False, False


###################### APIs ########################


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id')
    if 'is_admin' in session:
        session.pop('is_admin')
    return redirect('/login')


@app.route('/api/main/exp_weight')
def get_exp_weight():
    return requests.post(BACKEND_ADDRESS + "/weight", json=request.get_json()).json()


@app.route('/api/main/result')
def get_result():
    data = request.get_json()
    data['user_key'] = session['user_id']
    data['finish_time'] = datetime.now().strftime('%Y %m %d %H %M %S')
    
    requests.post(BACKEND_ADDRESS + "/save/weight", json=data)
    
    return 'saved'


# User Api
@app.route('/api/admin/has_id', methods=['POST'])
def can_use_this_id():
    data = request.get_json()
    req = requests.post(BACKEND_ADDRESS + "/user/has_id", json=data).json()
    return req


@app.route('/api/admin/make_user', methods=['POST'])
def make_user():
    data = request.get_json()
    data['password'] = encrypt(data['password'])
    requests.post(BACKEND_ADDRESS + "/user/make_user", json=data)
    return 'saved'


@app.route('/api/admin/update_password', methods=['POST'])
def update_password():
    data = request.get_json()
    data['password'] = encrypt(data['password'])
    requests.post(BACKEND_ADDRESS + "/user/update_password", json=data)
    return 'saved'


@app.route('/api/admin/get_users', methods=['GET'])
def get_users():
    data = request.get_json()
    req = requests.post(BACKEND_ADDRESS + "/user/login_info", json=data).json()
    return req


################# T  E  S  T ##################


@app.route('/api/bi')
def get_bcrypt_str():
    password = request.args.get('pw')
    bcrypt_pw = encrypt(password)
    
    return bcrypt_pw


@app.route('/api/test1')
def test():
    return {"path": request.path, "host": request.host_url}


@app.route('/api/test2')
def test2():
    return requests.post(BACKEND_ADDRESS + "/get/password", json={'user_id': "A00004689"}).text


if __name__ == "__main__":
    app.run()
